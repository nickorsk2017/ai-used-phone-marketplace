"""Ranking rules of the search, no I/O: docs/ai/RERANKING.md."""

import uuid
from collections.abc import Sequence

from modules.rag.schemas.search import Candidate, RerankOutput

RESULTS_LIMIT = 20
DIVERSITY_LIMIT = 5
# Better condition first when the prompt does not set it: docs/features/SEARCH_PAGE.md#condition-and-price.
CONDITION_RANK = {"like_new": 0, "average": 1, "for_repair": 2}
# Relevance rounded to this step counts as "close": the condition preference decides inside it.
RELEVANCE_STEP = 0.05


def merge(by_code: Sequence[Candidate], by_vector: Sequence[Candidate]) -> list[Candidate]:
    """Deduplication by `phone_id`, the first occurrence (model code path) is kept."""
    merged: dict[uuid.UUID, Candidate] = {}
    for candidate in [*by_code, *by_vector]:
        merged.setdefault(candidate.phone_id, candidate)
    return list(merged.values())


def validate_scores(output: RerankOutput, candidates: Sequence[Candidate]) -> dict[uuid.UUID, float]:
    """Output validation: docs/ai/RERANKING.md#output-validation. Missing candidates get 0."""
    known = {str(candidate.phone_id): candidate.phone_id for candidate in candidates}
    scores: dict[uuid.UUID, float] = {}
    for item in output.results:
        phone_id = known.get(item.phone_id.strip().lower())
        if phone_id is not None and phone_id not in scores:
            scores[phone_id] = item.relevance
    return {candidate.phone_id: scores.get(candidate.phone_id, 0.0) for candidate in candidates}


def _condition_key(candidate: Candidate, prefer_condition: bool) -> int:
    return CONDITION_RANK[candidate.condition] if prefer_condition else 0


def rank(
    candidates: Sequence[Candidate], scores: dict[uuid.UUID, float], threshold: float, prefer_condition: bool
) -> list[Candidate]:
    """Threshold, then relevance, the condition preference at close relevance, then the lower price."""
    kept = [candidate for candidate in candidates if scores[candidate.phone_id] >= threshold]
    return sorted(
        kept,
        key=lambda candidate: (
            -round(scores[candidate.phone_id] / RELEVANCE_STEP),
            _condition_key(candidate, prefer_condition),
            candidate.price,
        ),
    )


def fallback_order(candidates: Sequence[Candidate], prefer_condition: bool) -> list[Candidate]:
    """Order without the reranker: docs/ai/RERANKING.md#errors."""
    by_code = [candidate for candidate in candidates if candidate.source == "model_code"]
    by_vector = [candidate for candidate in candidates if candidate.source == "vector"]
    by_code.sort(key=lambda candidate: (_condition_key(candidate, prefer_condition), candidate.price))
    by_vector.sort(
        key=lambda candidate: (
            candidate.distance if candidate.distance is not None else 0.0,
            _condition_key(candidate, prefer_condition),
        )
    )
    return [*by_code, *by_vector]


def diversity_limit(ranked: Sequence[Candidate], single_model: bool) -> list[Candidate]:
    """At most 5 listings of one `model_code` in the top, the rest moved after: docs/ai/RERANKING.md#diversity-limit."""
    if single_model:
        return list(ranked)
    counts: dict[str, int] = {}
    head: list[Candidate] = []
    tail: list[Candidate] = []
    for candidate in ranked:
        counts[candidate.model_code] = counts.get(candidate.model_code, 0) + 1
        (head if counts[candidate.model_code] <= DIVERSITY_LIMIT else tail).append(candidate)
    return [*head, *tail]


def top(ranked: Sequence[Candidate]) -> list[uuid.UUID]:
    return [candidate.phone_id for candidate in ranked[:RESULTS_LIMIT]]
