"""Step `phones.hallucinated_models`: a model that does not exist returns no description (HTTP 422 of the endpoint),
docs/ai/EVALUATION.md#datasets. Same target as `phones.description`."""

from typing import Any

from pydantic import BaseModel, Field

from eval.metrics import Outputs, result
from eval.phones.description import target
from eval.schemas import EvalDataset, Example

# Cases


class HallucinatedCase(BaseModel):
    model_name: str = Field(min_length=1)

    def example(self) -> Example:
        return Example(inputs={"model_name": self.model_name}, outputs={"description": None})


CASES: list[HallucinatedCase] = [
    HallucinatedCase(model_name="iPhone 25"),
    HallucinatedCase(model_name="iPhone 11 Ultra"),
    HallucinatedCase(model_name="Galaxy S99"),
    HallucinatedCase(model_name="Galaxy Z Fold20"),
    HallucinatedCase(model_name="Pixel 42 Pro"),
    HallucinatedCase(model_name="Xiaomi 95 Ultra"),
    HallucinatedCase(model_name="OnePlus 77"),
    HallucinatedCase(model_name="Huawei Mate 500"),
    HallucinatedCase(model_name="Motorola Razr 2099"),
    HallucinatedCase(model_name="Nothing Phone (30)"),
]

# Metrics


def no_description(outputs: Outputs) -> dict[str, Any]:
    """A valid output without a description: the endpoint returns HTTP 422."""
    return result("no_description", "error" not in outputs and outputs.get("description") is None)


DATASET = EvalDataset(
    name="phones.hallucinated_models",
    examples=[case.example() for case in CASES],
    target=target,
    metrics=[no_description],
)
