"""Shared shapes of the evaluation: docs/backend/STRUCTURE.md#eval. Case shapes live in the file of their step."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

DATASET_MIN_CASES = 10
DATASET_MAX_CASES = 20

Target = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]
Metric = Callable[..., dict[str, Any]]


class Example(BaseModel):
    """A LangSmith example: `inputs` of the target and `outputs`, the reference for the metrics."""

    inputs: dict[str, Any]
    outputs: dict[str, Any]


@dataclass(frozen=True)
class EvalDataset:
    """One evaluated AI step. `name` is `<module>.<step>`: docs/ai/EVALUATION.md#datasets."""

    name: str
    examples: list[Example]
    target: Target
    metrics: list[Metric]
    # Runs on the evaluation database: docs/ai/EVALUATION.md#evaluation-database.
    needs_database: bool = False
