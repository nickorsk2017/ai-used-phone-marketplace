"""Step `phones.description`: model data generation, docs/features/MY_LISTING.md#description-response,
docs/ai/EVALUATION.md#datasets.

The expected model data is the seed listing of the same model name, so the seed stays the single source of it.
"""

from typing import Any

from pydantic import BaseModel

from core.llm import INVALID_LLM_OUTPUT
from eval.metrics import Outputs, result, valid_output
from eval.schemas import EvalDataset, Example
from modules.phones import services as phones_service
from modules.phones.schemas import PhoneCreate
from seed.run import LISTINGS

BATTERY_TOLERANCE = 0.05
DISPLAY_TOLERANCE_INCHES = 0.1

# Cases


class DescriptionCase(BaseModel):
    phone: PhoneCreate

    def example(self) -> Example:
        expected = self.phone.model_dump(
            mode="json", include={"model_code", "os", "camera_megapixels", "battery_capacity", "display_size"}
        )
        return Example(inputs={"model_name": self.phone.model_name}, outputs=expected)


MODEL_NAMES = [
    "iPhone 12",
    "iPhone 14 Pro",
    "iPhone 16e",
    "iPhone 17 Pro Max",
    "Galaxy S23 FE",
    "Galaxy S25 Ultra",
    "Galaxy Z Flip6",
    "Galaxy A36 5G",
    "Pixel 8a",
    "Pixel 10 Pro",
    "OnePlus 13",
    "Xiaomi 15T Pro",
    "Huawei Pura 80 Pro",
    "Oppo Find X9",
    "Nothing Phone (3)",
]

_SEED_PHONES = {listing.phone.model_name: listing.phone for listing in LISTINGS}

CASES: list[DescriptionCase] = [DescriptionCase(phone=_SEED_PHONES[name]) for name in MODEL_NAMES]

# Target


async def target(inputs: dict[str, Any]) -> dict[str, Any]:
    """`phones.services.generate_description`. An invalid output left after the repeat is returned as `error`."""
    try:
        generated = await phones_service.generate_description(inputs["model_name"])
    except INVALID_LLM_OUTPUT as error:
        return {"error": type(error).__name__}
    return {"description": None if generated is None else generated.model_dump(mode="json")}


# Metrics


def _field_match(key: str, outputs: Outputs, reference_outputs: Outputs) -> dict[str, Any]:
    description = outputs.get("description")
    if description is None:
        return result(key, False)
    return result(key, description[key] == reference_outputs[key])


def model_code_match(outputs: Outputs, reference_outputs: Outputs) -> dict[str, Any]:
    return _field_match("model_code", outputs, reference_outputs)


def os_match(outputs: Outputs, reference_outputs: Outputs) -> dict[str, Any]:
    return _field_match("os", outputs, reference_outputs)


def specifications_close(outputs: Outputs, reference_outputs: Outputs) -> dict[str, Any]:
    """Camera equal, battery within 5%, display within 0.1 inch."""
    description = outputs.get("description")
    if description is None:
        return result("specifications", False)
    battery = reference_outputs["battery_capacity"]
    close = (
        description["camera_megapixels"] == reference_outputs["camera_megapixels"]
        and abs(description["battery_capacity"] - battery) <= battery * BATTERY_TOLERANCE
        and abs(description["display_size"] - reference_outputs["display_size"]) <= DISPLAY_TOLERANCE_INCHES + 1e-9
    )
    return result("specifications", close)


DATASET = EvalDataset(
    name="phones.description",
    examples=[case.example() for case in CASES],
    target=target,
    metrics=[valid_output, model_code_match, os_match, specifications_close],
)
