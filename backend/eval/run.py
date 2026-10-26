"""`make eval`: the datasets of all modules and the results table: docs/ai/EVALUATION.md#run.

Run from `backend/`: `python -m eval.run [--dataset NAME] [--local]`. Real OpenAI calls.
`--local` runs the targets and the metrics without LangSmith: no upload, no experiment, no traces.
"""

import argparse
import asyncio
import inspect
import statistics
import sys
import time
from dataclasses import dataclass, field
from typing import Any

from langsmith import Client, aevaluate, tracing_context

from core.database import get_engine
from core.tracing import configure_tracing
from eval import phones, rag
from eval.database import prepare_eval_database
from eval.schemas import EvalDataset, Example, Metric
from eval.upload import upload
from modules.phones.config import config_errors as phones_config_errors
from modules.phones.config import get_settings as get_phones_settings
from modules.rag.config import config_errors as rag_config_errors
from modules.rag.config import get_settings as get_rag_settings

MAX_CONCURRENCY = 4
STATS_ATTEMPTS = 5
STATS_WAIT_SECONDS = 3

# All evaluated steps by `<module>.<step>`: docs/backend/STRUCTURE.md#eval.
DATASETS: dict[str, EvalDataset] = {dataset.name: dataset for dataset in [*rag.DATASETS, *phones.DATASETS]}


@dataclass
class DatasetReport:
    dataset: str
    experiment: str | None = None
    scores: dict[str, list[float]] = field(default_factory=dict)
    latencies: list[float] = field(default_factory=list)
    errors: int = 0
    tokens: int | None = None
    cost: float | None = None

    def add_score(self, key: str, score: float | None) -> None:
        if score is not None:
            self.scores.setdefault(key, []).append(float(score))


def models_metadata() -> dict[str, str]:
    """Models of the evaluated steps, stored with the experiment for the comparison of runs."""
    phones_settings, rag_settings = get_phones_settings(), get_rag_settings()
    return {
        "description_model": phones_settings.description_model,
        "search_model": rag_settings.search_model,
        "rerank_model": rag_settings.rerank_model,
    }


def percentile(values: list[float], share: float) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    return statistics.quantiles(values, n=100, method="inclusive")[round(share * 100) - 1]


# LangSmith


async def run_langsmith(client: Client, project: str, dataset: EvalDataset) -> DatasetReport:
    name = upload(client, project, dataset)
    results = await aevaluate(
        dataset.target,
        data=name,
        evaluators=dataset.metrics,
        experiment_prefix=dataset.name,
        metadata=models_metadata(),
        max_concurrency=MAX_CONCURRENCY,
        client=client,
    )
    report = DatasetReport(dataset=dataset.name, experiment=results.experiment_name)
    async for row in results:
        run = row["run"]
        if run.error:
            report.errors += 1
        if run.end_time is not None:
            report.latencies.append((run.end_time - run.start_time).total_seconds())
        for result in row["evaluation_results"]["results"]:
            report.add_score(result.key, result.score)
    await read_usage(client, report)
    return report


async def read_usage(client: Client, report: DatasetReport) -> None:
    """Tokens and cost of the experiment: LangSmith computes them after the runs are ingested."""
    client.flush()
    for _ in range(STATS_ATTEMPTS):
        stats = client.read_project(project_name=report.experiment, include_stats=True)
        if stats.total_tokens:
            report.tokens = stats.total_tokens
            report.cost = float(stats.total_cost) if stats.total_cost is not None else None
            return
        await asyncio.sleep(STATS_WAIT_SECONDS)


# Local


def apply_metric(metric: Metric, example: Example, outputs: dict[str, Any]) -> dict[str, Any]:
    """Calls the metric with the arguments it declares, as LangSmith does."""
    available = {"inputs": example.inputs, "outputs": outputs, "reference_outputs": example.outputs}
    return metric(**{name: available[name] for name in inspect.signature(metric).parameters})


async def run_local(dataset: EvalDataset) -> DatasetReport:
    report = DatasetReport(dataset=dataset.name)
    limit = asyncio.Semaphore(MAX_CONCURRENCY)

    async def one(example: Example) -> None:
        async with limit:
            started = time.perf_counter()
            try:
                outputs = await dataset.target(example.inputs)
            except Exception:
                report.errors += 1
                return
            report.latencies.append(time.perf_counter() - started)
        for metric in dataset.metrics:
            result = apply_metric(metric, example, outputs)
            report.add_score(result["key"], result["score"])

    await asyncio.gather(*(one(example) for example in dataset.examples))
    return report


# Table


def _number(value: float | None, pattern: str) -> str:
    return "n/a" if value is None else pattern.format(value)


def table(reports: list[DatasetReport]) -> str:
    header = ("Dataset", "Metric", "Score", "Cases", "p50 s", "p95 s", "Errors", "Tokens", "Cost $")
    rows = [header]
    for report in reports:
        p50, p95 = percentile(report.latencies, 0.5), percentile(report.latencies, 0.95)
        for key, scores in report.scores.items():
            rows.append(
                (
                    report.dataset,
                    key,
                    f"{statistics.fmean(scores):.2f}",
                    str(len(scores)),
                    _number(p50, "{:.2f}"),
                    _number(p95, "{:.2f}"),
                    str(report.errors),
                    _number(report.tokens, "{:d}"),
                    _number(report.cost, "{:.4f}"),
                )
            )
    widths = [max(len(row[index]) for row in rows) for index in range(len(header))]
    return "\n".join("  ".join(cell.ljust(width) for cell, width in zip(row, widths, strict=True)) for row in rows)


# Entry point


def check_config() -> None:
    """Only the settings of the evaluated modules: `make eval LOCAL=1` needs `OPENAI_API_KEY` only."""
    errors = list(dict.fromkeys([*phones_config_errors(), *rag_config_errors()]))
    if errors:
        raise SystemExit(
            "make eval: missing or invalid environment variables:\n" + "\n".join(f"  - {e}" for e in errors)
        )


async def main(names: list[str], local: bool) -> None:
    check_config()
    datasets = [DATASETS[name] for name in names]
    try:
        if any(dataset.needs_database for dataset in datasets):
            await prepare_eval_database()
        if local:
            configure_tracing()
            with tracing_context(enabled=False):
                reports = [await run_local(dataset) for dataset in datasets]
        else:
            project = configure_tracing(force=True).langsmith_project
            client = Client()
            reports = [await run_langsmith(client, project, dataset) for dataset in datasets]
    finally:
        if get_engine.cache_info().currsize:
            await get_engine().dispose()
    print(table(reports))
    for report in reports:
        if report.experiment is not None:
            print(f"{report.dataset}: experiment {report.experiment}")


def parse_args(argv: list[str]) -> tuple[list[str], bool]:
    parser = argparse.ArgumentParser(description="LLM evaluation: docs/ai/EVALUATION.md#run")
    parser.add_argument("--dataset", choices=list(DATASETS), help="run one dataset, all datasets by default")
    parser.add_argument("--local", action="store_true", help="run without LangSmith")
    args = parser.parse_args(argv)
    return ([args.dataset] if args.dataset else list(DATASETS)), args.local


if __name__ == "__main__":
    try:
        asyncio.run(main(*parse_args(sys.argv[1:])))
    except ValueError as error:
        raise SystemExit(f"make eval: {error}. Set it in backend/.env.") from error
