"""Metrics of the steps, docs/ai/EVALUATION.md#datasets: 1, 0, or `None` when the case does not set the field."""

import conftest  # noqa: F401  # test environment: no traces, stub keys
from eval import metrics
from eval.phones import description, hallucinated_models
from eval.rag import clarification, parse

PARSED = {
    "filters": {
        "condition": {"value": ["average", "like_new"]},
        "price": {"operator": ">=", "value": 400, "max_value": 600},
    },
    "preferences": {"os": {"value": "ios"}},
    "query_for_embedding": "iPhone",
}
EMPTY = {"filters": {}, "preferences": {}, "query_for_embedding": "phone"}
ERROR = {"error": "ValidationError"}
SEED = {"model_code": "A2172", "os": "ios", "camera_megapixels": 12, "battery_capacity": 2815, "display_size": 6.1}


def score(result: dict) -> int | None:
    return result["score"]


def test_valid_output() -> None:
    assert score(metrics.valid_output({"parsed": PARSED})) == 1
    assert score(metrics.valid_output(ERROR)) == 0


def test_condition_is_compared_as_a_set() -> None:
    reference = {"condition": ["like_new", "average"]}
    assert score(parse.condition_match({"parsed": PARSED}, reference)) == 1
    assert score(parse.condition_match({"parsed": PARSED}, {"condition": ["like_new"]})) == 0


def test_null_means_the_field_must_be_absent() -> None:
    assert score(parse.condition_match({"parsed": EMPTY}, {"condition": None})) == 1
    assert score(parse.condition_match({"parsed": PARSED}, {"condition": None})) == 0
    assert score(parse.price_match({"parsed": PARSED}, {"price": None})) == 0
    assert score(parse.os_match({"parsed": EMPTY}, {"os": None})) == 1


def test_unset_field_is_not_checked() -> None:
    assert score(parse.os_match({"parsed": PARSED}, {"condition": None})) is None
    assert score(parse.price_match(ERROR, {})) is None


def test_price_compares_operator_value_and_max_value() -> None:
    assert (
        score(parse.price_match({"parsed": PARSED}, {"price": {"operator": ">=", "value": 400, "max_value": 600}})) == 1
    )
    assert score(parse.price_match({"parsed": PARSED}, {"price": {"operator": ">=", "value": 400}})) == 0
    assert (
        score(parse.price_match({"parsed": PARSED}, {"price": {"operator": "<=", "value": 400, "max_value": 600}})) == 0
    )
    single = {"parsed": {**EMPTY, "filters": {"price": {"operator": "<=", "value": 300}}}}
    assert score(parse.price_match(single, {"price": {"operator": "<=", "value": 300}})) == 1


def test_os_match() -> None:
    assert score(parse.os_match({"parsed": PARSED}, {"os": "ios"})) == 1
    assert score(parse.os_match({"parsed": PARSED}, {"os": "android"})) == 0


def test_invalid_output_scores_0_on_a_checked_field() -> None:
    assert score(parse.condition_match(ERROR, {"condition": None})) == 0


def test_clarification_returned_when_expected_and_only_then() -> None:
    asked = {"parsed": {"clarification": "What is your budget?", "filters": {}, "preferences": {}}}
    assert score(clarification.clarification_match(asked, {"clarification": True})) == 1
    assert score(clarification.clarification_match({"parsed": EMPTY}, {"clarification": True})) == 0
    assert score(clarification.clarification_match({"parsed": EMPTY}, {"clarification": False})) == 1
    assert score(clarification.clarification_match(asked, {"clarification": False})) == 0
    assert score(clarification.clarification_match(ERROR, {"clarification": False})) == 0


def test_model_code_and_os_match() -> None:
    assert score(description.model_code_match({"description": SEED}, SEED)) == 1
    assert score(description.model_code_match({"description": {**SEED, "model_code": "A2403"}}, SEED)) == 0
    assert score(description.os_match({"description": {**SEED, "os": "android"}}, SEED)) == 0
    assert score(description.model_code_match({"description": None}, SEED)) == 0


def test_specifications_tolerances() -> None:
    def close(**changes: object) -> int | None:
        return score(description.specifications_close({"description": {**SEED, **changes}}, SEED))

    assert close() == 1
    assert close(battery_capacity=2955) == 1
    assert close(battery_capacity=2957) == 0
    assert close(battery_capacity=2675) == 1
    assert close(display_size=6.2) == 1
    assert close(display_size=6.25) == 0
    assert close(camera_megapixels=48) == 0
    assert score(description.specifications_close({"description": None}, SEED)) == 0


def test_no_description() -> None:
    assert score(hallucinated_models.no_description({"description": None})) == 1
    assert score(hallucinated_models.no_description({"description": SEED})) == 0
    assert score(hallucinated_models.no_description(ERROR)) == 0
