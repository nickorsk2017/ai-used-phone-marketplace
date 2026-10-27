"""Step `rag.search`: metric values computed by hand and the case rules, docs/ai/EVALUATION.md#ranking."""

import math

import pytest

import conftest  # noqa: F401  # test environment: no traces, stub keys
from eval.rag import ranking
from eval.rag.search import CASES, DATASET, hit_rate, ndcg, precision, recall, reciprocal_rank
from eval.schemas import DATASET_MAX_CASES, DATASET_MIN_CASES
from seed.run import LISTINGS

# The example of docs/ai/EVALUATION.md: A and B highly relevant, C and D relevant, D not found.
GRADES = {"A": 2, "B": 2, "C": 1, "D": 1}
RELEVANT = set(GRADES)
RANKED = ["A", "X", "C", "Y", "Z", "B", *[f"N{index}" for index in range(14)]]


def test_documented_example() -> None:
    assert hit_rate(RANKED, RELEVANT, 5) == 1
    assert precision(RANKED, RELEVANT, 5) == pytest.approx(0.5)
    assert recall(RANKED, RELEVANT, 20) == pytest.approx(0.75)
    assert reciprocal_rank(RANKED, RELEVANT) == 1
    dcg = 3 + 1 / math.log2(4) + 3 / math.log2(7)
    ideal = 3 + 3 / math.log2(3) + 1 / math.log2(4) + 1 / math.log2(5)
    assert ndcg(RANKED, GRADES, 10) == pytest.approx(dcg / ideal)
    assert round(ndcg(RANKED, GRADES, 10), 2) == 0.78


def test_no_results() -> None:
    assert hit_rate([], RELEVANT, 5) == 0
    assert precision([], RELEVANT, 5) == 0
    assert recall([], RELEVANT, 20) == 0
    assert reciprocal_rank([], RELEVANT) == 0
    assert ndcg([], GRADES, 10) == 0


def test_no_relevant_listing_found() -> None:
    ranked = ["X", "Y", "Z"]
    assert (hit_rate(ranked, RELEVANT, 5), recall(ranked, RELEVANT, 20), reciprocal_rank(ranked, RELEVANT)) == (0, 0, 0)
    assert ndcg(ranked, GRADES, 10) == 0


def test_relevant_listings_below_the_cut_off() -> None:
    ranked = ["X1", "X2", "X3", "X4", "X5", "A"]
    assert hit_rate(ranked, RELEVANT, 5) == 0
    assert precision(ranked, RELEVANT, 5) == 0
    assert reciprocal_rank(ranked, RELEVANT) == pytest.approx(1 / 6)
    assert recall(ranked, RELEVANT, 20) == pytest.approx(0.25)
    assert ndcg(["X"] * 10 + ["A"], GRADES, 10) == 0


def test_fewer_results_than_k() -> None:
    assert precision(["A", "B"], RELEVANT, 5) == pytest.approx(0.5)
    assert precision(["A", "B"], {"A", "B"}, 5) == pytest.approx(1)
    assert recall(["A", "B"], RELEVANT, 20) == pytest.approx(0.5)


def test_ndcg_rewards_the_higher_grade_first() -> None:
    assert ndcg(["A", "B", "C", "D"], GRADES, 10) == pytest.approx(1)
    assert ndcg(["C", "D", "A", "B"], GRADES, 10) < ndcg(["A", "C", "B", "D"], GRADES, 10) < 1


def test_metric_wrappers_use_the_grades_and_the_cut_offs() -> None:
    outputs, reference = {"ranked": RANKED}, {"grades": GRADES}
    scores = {metric(outputs, reference)["key"]: metric(outputs, reference)["score"] for metric in DATASET.metrics}
    assert list(scores) == ["hit_rate@5", "precision@5", "recall@20", "mrr", "ndcg@10"]
    assert scores["precision@5"] == pytest.approx(0.5)
    assert scores["recall@20"] == pytest.approx(0.75)


def test_clarification_or_blocked_prompt_scores_0() -> None:
    for outputs in ({"ranked": [], "clarification": "Budget?"}, {"ranked": [], "error": "PromptBlocked"}):
        assert all(metric(outputs, {"grades": GRADES})["score"] == 0 for metric in DATASET.metrics)


def test_ranking_runs_one_request_at_a_time() -> None:
    assert DATASET.max_concurrency == 1


def test_case_count() -> None:
    assert DATASET_MIN_CASES <= len(CASES) <= DATASET_MAX_CASES
    assert len({case.prompt for case in CASES}) == len(CASES)


@pytest.mark.parametrize("case", CASES, ids=[case.prompt for case in CASES])
def test_case_has_1_to_19_relevant_seed_listings(case: ranking.RankingCase) -> None:
    grades = case.grades([listing.phone for listing in LISTINGS])
    assert 1 <= len(grades) < ranking.RESULTS_LIMIT
    assert set(grades.values()) <= {ranking.RELEVANT, ranking.HIGHLY_RELEVANT}


@pytest.mark.parametrize("case", CASES, ids=[case.prompt for case in CASES])
def test_rule_is_not_only_price_and_condition(case: ranking.RankingCase) -> None:
    """Price and condition are applied in SQL. With the same price and condition for every listing, a rule that
    checks only them selects all listings or none: the rule must still select some listings and not others."""
    phones = [listing.phone for listing in LISTINGS]

    def selected(condition: str) -> int:
        return sum(case.relevant(phone.model_copy(update={"price": 1, "condition": condition})) for phone in phones)

    assert any(0 < selected(condition) < len(phones) for condition in ("like_new", "average", "for_repair"))


def test_example_outputs_are_the_grades() -> None:
    example = CASES[2].example()
    assert example.inputs == {"prompt": "iPhone 15 Pro"}
    assert example.outputs["grades"]["A2848"] == ranking.HIGHLY_RELEVANT
    assert example.outputs["grades"]["A2846"] == ranking.RELEVANT
