"""Runner of `make eval`: the table and the local mode, docs/ai/EVALUATION.md#run. No LLM, no LangSmith."""

import pytest

import conftest  # noqa: F401  # test environment: no traces, stub keys
from eval import run
from eval.metrics import valid_output
from eval.run import DatasetReport, apply_metric, parse_args, percentile, run_local, table
from eval.schemas import EvalDataset, Example

ALL = ["rag.parse", "rag.clarification", "rag.ranking", "phones.description", "phones.hallucinated_models"]


def test_percentiles() -> None:
    values = [float(value) for value in range(1, 21)]
    assert percentile(values, 0.5) == pytest.approx(10.5)
    assert percentile(values, 0.95) == pytest.approx(19.05)
    assert percentile([2.0], 0.95) == 2.0
    assert percentile([], 0.5) is None


def test_table_has_one_row_per_metric_with_the_mean() -> None:
    report = DatasetReport(
        dataset="rag.ranking",
        experiment="rag.ranking-1",
        scores={"valid_output": [1, 1, 1, 0], "ndcg@10": [0.78, 0.5]},
        latencies=[1.0, 2.0],
        tokens=1200,
        cost=0.0123,
    )
    lines = table([report]).splitlines()
    assert lines[0].split()[:4] == ["Dataset", "Metric", "Score", "Cases"]
    assert lines[1].split()[:4] == ["rag.ranking", "valid_output", "0.75", "4"]
    assert lines[2].split()[:4] == ["rag.ranking", "ndcg@10", "0.64", "2"]
    assert lines[1].split()[-2:] == ["1200", "0.0123"]


def test_usage_not_available_locally() -> None:
    report = DatasetReport(dataset="rag.parse", scores={"valid_output": [1]})
    assert table([report]).splitlines()[1].split()[-4:] == ["n/a", "0", "n/a", "n/a"]


def test_arguments() -> None:
    assert parse_args([]) == (ALL, False)
    assert parse_args(["--dataset", "rag.parse", "--local"]) == (["rag.parse"], True)
    with pytest.raises(SystemExit):
        parse_args(["--dataset", "unknown"])


def test_only_ranking_needs_the_database() -> None:
    assert [name for name, dataset in run.DATASETS.items() if dataset.needs_database] == ["rag.ranking"]


def test_metric_gets_the_arguments_it_declares() -> None:
    example = Example(inputs={"prompt": "x"}, outputs={"grades": {}})

    def uses_all(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
        return {"key": "all", "score": float(inputs == example.inputs and reference_outputs == example.outputs)}

    assert apply_metric(valid_output, example, {"error": "ValidationError"})["score"] == 0
    assert apply_metric(uses_all, example, {})["score"] == 1


async def test_local_run_applies_the_metrics_without_langsmith(monkeypatch: pytest.MonkeyPatch) -> None:
    def no_client(*args: object, **kwargs: object) -> None:
        raise AssertionError("the local run creates no LangSmith client")

    monkeypatch.setattr(run, "Client", no_client)

    async def target(inputs: dict) -> dict:
        if inputs["prompt"] == "fails":
            raise RuntimeError("provider down")
        return {"error": "ValidationError"} if inputs["prompt"] == "invalid" else {"parsed": {}}

    prompts = ["ok", "ok too", "invalid", "fails"]
    dataset = EvalDataset(
        name="rag.parse",
        examples=[Example(inputs={"prompt": prompt}, outputs={}) for prompt in prompts],
        target=target,
        metrics=[valid_output],
    )
    report = await run_local(dataset)
    assert report.errors == 1
    assert sorted(report.scores["valid_output"]) == [0.0, 1.0, 1.0]
    assert len(report.latencies) == 3
    assert report.tokens is None and report.experiment is None
