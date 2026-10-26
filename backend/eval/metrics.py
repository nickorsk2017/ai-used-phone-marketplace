"""Metrics shared by several steps: docs/ai/EVALUATION.md#datasets.

LangSmith passes the target output as `outputs` and the reference of the example as `reference_outputs`.
A metric returns the score 1 or 0, or `None` when the case does not set the checked field.
"""

from typing import Any

Outputs = dict[str, Any]


def result(key: str, score: bool | None) -> dict[str, Any]:
    return {"key": key, "score": None if score is None else int(score)}


def valid_output(outputs: Outputs) -> dict[str, Any]:
    """The output passed the schema validation, after the repeat on an invalid output."""
    return result("valid_output", "error" not in outputs)
