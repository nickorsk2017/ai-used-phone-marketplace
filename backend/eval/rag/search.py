"""Step `rag.search`: the whole search on the seed, docs/ai/EVALUATION.md#ranking.

The relevant listings of a case are computed from the seed by rules, identified by `model_code`, with the grade
2 (highly relevant) or 1 (relevant). The search runs on the evaluation database:
docs/ai/EVALUATION.md#evaluation-database.
"""

import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from core.database import transaction
from eval.metrics import Outputs
from eval.schemas import EvalDataset, Example
from modules.phones import services as phones_service
from modules.phones.schemas import PhoneCreate
from modules.rag import services as rag_service
from modules.rag.schemas.search import PromptBlocked
from seed.run import LISTINGS

TOP_SCREEN = 5
NDCG_CUTOFF = 10
RESULTS_LIMIT = 20
RELEVANT, HIGHLY_RELEVANT = 1, 2

Rule = Callable[[PhoneCreate], bool]

# Cases


def _brand(*prefixes: str) -> Rule:
    return lambda phone: phone.model_name.startswith(prefixes)


@dataclass(frozen=True)
class RankingCase:
    """`highly_relevant` is applied to the relevant listings only, so it is always a subset of `relevant`."""

    prompt: str
    relevant: Rule
    highly_relevant: Rule | None = None

    def grades(self, phones: list[PhoneCreate]) -> dict[str, int]:
        return {
            phone.model_code: HIGHLY_RELEVANT
            if self.highly_relevant is not None and self.highly_relevant(phone)
            else RELEVANT
            for phone in phones
            if self.relevant(phone)
        }

    def example(self) -> Example:
        return Example(
            inputs={"prompt": self.prompt},
            outputs={"grades": self.grades([listing.phone for listing in LISTINGS])},
        )


CASES: list[RankingCase] = [
    RankingCase(
        prompt="Android with a battery of 6500 mAh or more under $400",
        relevant=lambda p: p.os == "android" and p.battery_capacity >= 6500 and p.price <= 400,
        highly_relevant=lambda p: p.battery_capacity >= 7000,
    ),
    RankingCase(
        prompt="Android con batería de 7000 mAh o más",
        relevant=lambda p: p.os == "android" and p.battery_capacity >= 7000,
    ),
    RankingCase(
        prompt="iPhone 15 Pro",
        relevant=_brand("iPhone 15"),
        highly_relevant=lambda p: p.model_name == "iPhone 15 Pro",
    ),
    RankingCase(
        prompt="Pixel 10 Pro",
        relevant=_brand("Pixel 10"),
        highly_relevant=lambda p: p.model_name == "Pixel 10 Pro",
    ),
    RankingCase(prompt="Samsung Galaxy S25 series", relevant=_brand("Galaxy S25")),
    RankingCase(prompt="Samsung foldable phone", relevant=_brand("Galaxy Z")),
    RankingCase(prompt="Phone with a 200 MP camera", relevant=lambda p: p.camera_megapixels == 200),
    RankingCase(
        prompt="iPhone with a 48 MP camera, like new, under $500",
        relevant=lambda p: p.os == "ios" and p.camera_megapixels == 48 and p.condition == "like_new" and p.price <= 500,
    ),
    RankingCase(
        prompt="Phone with a big screen of 6.9 inches or more under $700",
        relevant=lambda p: p.display_size >= 6.9 and p.price <= 700,
    ),
    RankingCase(
        prompt="Compact phone with a small screen",
        relevant=lambda p: p.display_size <= 6.1,
        highly_relevant=lambda p: p.display_size < 5.5,
    ),
    RankingCase(prompt="Cheap Google Pixel under $200", relevant=lambda p: _brand("Pixel")(p) and p.price <= 200),
    RankingCase(prompt="Xiaomi or POCO", relevant=_brand("Xiaomi", "POCO")),
    RankingCase(prompt="Huawei phone", relevant=_brand("Huawei")),
    RankingCase(
        prompt="Nothing phone in like new or average condition",
        relevant=lambda p: _brand("Nothing", "CMF")(p) and p.condition in ("like_new", "average"),
    ),
    RankingCase(
        prompt="iPhone 16 or iPhone 17 under $700",
        relevant=lambda p: _brand("iPhone 16", "iPhone 17")(p) and p.price <= 700,
    ),
]

# Target


async def target(inputs: dict[str, Any]) -> dict[str, Any]:
    """`rag.services.search` on the evaluation database. The result IDs become model codes in the search order."""
    async for session in transaction():
        try:
            result = await rag_service.search(session, inputs["prompt"])
        except PromptBlocked:
            return {"ranked": [], "error": "PromptBlocked"}
        if result.clarification is not None:
            return {"ranked": [], "clarification": result.clarification}
        phones = await phones_service.get_phones(session, result.phone_ids)
        return {"ranked": [phone.model_code for phone in phones]}
    raise AssertionError("unreachable: transaction() yields one session")


# Metrics: docs/ai/EVALUATION.md#metrics


def hit_rate(ranked: list[str], relevant: set[str], k: int) -> float:
    return float(any(item in relevant for item in ranked[:k]))


def precision(ranked: list[str], relevant: set[str], k: int) -> float:
    """Divided by `min(k, len(relevant))`: a case with fewer than `k` relevant listings can score 1.
    Divided by it also when the search returns fewer than `k` results."""
    return sum(item in relevant for item in ranked[:k]) / min(k, len(relevant))


def recall(ranked: list[str], relevant: set[str], k: int) -> float:
    """Against all relevant listings of the seed, found or not."""
    return sum(item in relevant for item in ranked[:k]) / len(relevant)


def reciprocal_rank(ranked: list[str], relevant: set[str]) -> float:
    return next((1 / rank for rank, item in enumerate(ranked, 1) if item in relevant), 0.0)


def _dcg(gains: list[int]) -> float:
    return sum((2**grade - 1) / math.log2(rank + 1) for rank, grade in enumerate(gains, 1))


def ndcg(ranked: list[str], grades: dict[str, int], k: int) -> float:
    """The ideal order is built from all relevant listings of the seed."""
    ideal = _dcg(sorted(grades.values(), reverse=True)[:k])
    return _dcg([grades.get(item, 0) for item in ranked[:k]]) / ideal


def _ranked(outputs: Outputs) -> list[str]:
    return outputs.get("ranked") or []


def hit_rate_at_5(outputs: Outputs, reference_outputs: Outputs) -> dict[str, Any]:
    return {"key": "hit_rate@5", "score": hit_rate(_ranked(outputs), set(reference_outputs["grades"]), TOP_SCREEN)}


def precision_at_5(outputs: Outputs, reference_outputs: Outputs) -> dict[str, Any]:
    return {"key": "precision@5", "score": precision(_ranked(outputs), set(reference_outputs["grades"]), TOP_SCREEN)}


def recall_at_20(outputs: Outputs, reference_outputs: Outputs) -> dict[str, Any]:
    return {"key": "recall@20", "score": recall(_ranked(outputs), set(reference_outputs["grades"]), RESULTS_LIMIT)}


def mrr(outputs: Outputs, reference_outputs: Outputs) -> dict[str, Any]:
    return {"key": "mrr", "score": reciprocal_rank(_ranked(outputs), set(reference_outputs["grades"]))}


def ndcg_at_10(outputs: Outputs, reference_outputs: Outputs) -> dict[str, Any]:
    return {"key": "ndcg@10", "score": ndcg(_ranked(outputs), reference_outputs["grades"], NDCG_CUTOFF)}


DATASET = EvalDataset(
    name="rag.search",
    examples=[case.example() for case in CASES],
    target=target,
    metrics=[hit_rate_at_5, precision_at_5, recall_at_20, mrr, ndcg_at_10],
    needs_database=True,
    max_concurrency=1,
    label="prompt to rerank",
)
