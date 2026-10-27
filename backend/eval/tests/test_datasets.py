"""Datasets of docs/ai/EVALUATION.md#datasets: size, shape and the seed as the expected model data."""

import pytest

import conftest  # noqa: F401  # test environment: no traces, stub keys
from eval.phones.description import MODEL_NAMES
from eval.run import DATASETS
from eval.schemas import DATASET_MAX_CASES, DATASET_MIN_CASES
from seed.run import LISTINGS


def test_the_documented_datasets_exist() -> None:
    assert list(DATASETS) == [
        "rag.parse",
        "rag.clarification",
        "rag.search",
        "phones.description",
        "phones.hallucinated_models",
    ]


@pytest.mark.parametrize("name", list(DATASETS))
def test_dataset_has_10_to_20_unique_cases(name: str) -> None:
    examples = DATASETS[name].examples
    assert DATASET_MIN_CASES <= len(examples) <= DATASET_MAX_CASES
    inputs = [tuple(sorted(example.inputs.items())) for example in examples]
    assert len(set(inputs)) == len(inputs)


@pytest.mark.parametrize("name", list(DATASETS))
def test_every_dataset_has_metrics_and_a_target(name: str) -> None:
    dataset = DATASETS[name]
    assert dataset.metrics
    assert callable(dataset.target)


def test_parse_cases_check_at_least_one_field() -> None:
    for example in DATASETS["rag.parse"].examples:
        assert set(example.outputs) <= {"condition", "price", "os"}
        assert example.outputs


def test_clarification_has_both_answers() -> None:
    answers = [example.outputs["clarification"] for example in DATASETS["rag.clarification"].examples]
    assert True in answers and False in answers


def test_description_cases_are_the_seed_listings() -> None:
    seed = {listing.phone.model_name: listing.phone for listing in LISTINGS}
    examples = DATASETS["phones.description"].examples
    assert [example.inputs["model_name"] for example in examples] == MODEL_NAMES
    for example in examples:
        phone = seed[example.inputs["model_name"]]
        assert example.outputs == {
            "model_code": phone.model_code,
            "os": phone.os,
            "camera_megapixels": phone.camera_megapixels,
            "battery_capacity": phone.battery_capacity,
            "display_size": phone.display_size,
        }


def test_description_covers_both_systems() -> None:
    assert {example.outputs["os"] for example in DATASETS["phones.description"].examples} == {"ios", "android"}


def test_hallucinated_models_are_not_in_the_seed() -> None:
    seed_names = {listing.phone.model_name for listing in LISTINGS}
    for example in DATASETS["phones.hallucinated_models"].examples:
        assert example.inputs["model_name"] not in seed_names
        assert example.outputs == {"description": None}


@pytest.mark.parametrize("name", list(DATASETS))
def test_dataset_name_is_module_dot_step(name: str) -> None:
    module, step = name.split(".")
    assert module in {"rag", "phones"}
    assert step
