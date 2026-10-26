"""Ranking rules: docs/ai/RERANKING.md."""

import uuid

from modules.rag.schemas.search import Candidate, RerankOutput, RerankScore
from modules.rag.services import ranking


def candidate(code: str = "A2483", condition: str = "like_new", price: int = 500, **extra: object) -> Candidate:
    return Candidate(
        phone_id=uuid.uuid4(),
        model_code=code,
        model_name="Phone",
        os="ios",
        camera_megapixels=12,
        battery_capacity=3000,
        display_size=6.1,
        description="",
        condition_note="",
        condition=condition,
        price=price,
        **extra,
    )


def test_merge_deduplicates_by_phone_id_keeping_the_model_code_path() -> None:
    first = candidate()
    copy = first.model_copy(update={"source": "vector", "distance": 0.1})
    other = candidate(source="vector", distance=0.2)
    merged = ranking.merge([first], [copy, other])
    assert [item.phone_id for item in merged] == [first.phone_id, other.phone_id]
    assert merged[0].source == "model_code"


def test_validate_scores_removes_unknown_and_repeated_ids_and_scores_missing_as_zero() -> None:
    a, b = candidate(), candidate()
    output = RerankOutput(
        results=[
            RerankScore(phone_id=str(a.phone_id), relevance=0.9),
            RerankScore(phone_id=str(a.phone_id), relevance=0.1),
            RerankScore(phone_id=str(uuid.uuid4()), relevance=1.0),
        ]
    )
    assert ranking.validate_scores(output, [a, b]) == {a.phone_id: 0.9, b.phone_id: 0.0}


def test_rank_applies_threshold_relevance_condition_and_price() -> None:
    low = candidate()
    repair = candidate(condition="for_repair", price=100)
    new_expensive = candidate(condition="like_new", price=900)
    new_cheap = candidate(condition="like_new", price=400)
    best = candidate(condition="for_repair")
    scores = {low.phone_id: 0.2, repair.phone_id: 0.8, new_expensive.phone_id: 0.8, new_cheap.phone_id: 0.8}
    scores[best.phone_id] = 0.95
    ranked = ranking.rank([low, repair, new_expensive, new_cheap, best], scores, 0.3, prefer_condition=True)
    assert ranked == [best, new_cheap, new_expensive, repair]


def test_rank_without_condition_preference_orders_by_price() -> None:
    repair = candidate(condition="for_repair", price=100)
    new = candidate(price=400)
    ranked = ranking.rank([new, repair], {repair.phone_id: 0.8, new.phone_id: 0.8}, 0.3, prefer_condition=False)
    assert ranked == [repair, new]


def test_diversity_limit_moves_listings_above_five_per_model_after_the_others() -> None:
    same = [candidate("A2483") for _ in range(7)]
    other = candidate("SM-S911U")
    limited = ranking.diversity_limit([*same, other], single_model=False)
    assert limited == [*same[:5], other, *same[5:]]


def test_diversity_limit_is_not_applied_for_one_model() -> None:
    same = [candidate("A2483") for _ in range(7)]
    assert ranking.diversity_limit(same, single_model=True) == same


def test_fallback_order_model_code_first_then_vector_by_distance() -> None:
    far = candidate(source="vector", distance=0.5)
    near = candidate(source="vector", distance=0.1)
    average = candidate(condition="average", price=100)
    new = candidate(price=900)
    assert ranking.fallback_order([far, average, near, new], prefer_condition=True) == [new, average, near, far]


def test_top_returns_at_most_twenty_ids() -> None:
    assert len(ranking.top([candidate() for _ in range(25)])) == 20
