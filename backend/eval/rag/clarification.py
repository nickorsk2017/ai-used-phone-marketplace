"""Step `rag.clarification`: docs/ai/RAG.md#clarification, docs/ai/EVALUATION.md#datasets.

`clarification=True`: the prompt has no phone criteria or asks for advice. Same target as `rag.parse`.
"""

from typing import Any

from pydantic import BaseModel, Field

from eval.metrics import Outputs, result, valid_output
from eval.rag.parse import target
from eval.schemas import EvalDataset, Example

# Cases


class ClarificationCase(BaseModel):
    prompt: str = Field(min_length=1)
    clarification: bool

    def example(self) -> Example:
        return Example(inputs={"prompt": self.prompt}, outputs={"clarification": self.clarification})


CASES: list[ClarificationCase] = [
    ClarificationCase(prompt="What phone should I give my wife for her birthday?", clarification=True),
    ClarificationCase(prompt="I need a new phone", clarification=True),
    ClarificationCase(prompt="Show me something nice", clarification=True),
    ClarificationCase(prompt="Looking for a gift for my dad", clarification=True),
    ClarificationCase(prompt="Hola, busco un teléfono", clarification=True),
    ClarificationCase(prompt="Any good deals today?", clarification=True),
    ClarificationCase(prompt="Which is better for games, iOS or Android?", clarification=True),
    ClarificationCase(
        prompt="What do you think is better for photos, a phone with a good camera or with a big screen?",
        clarification=True,
    ),
    ClarificationCase(prompt="Is it worth buying a used phone?", clarification=True),
    ClarificationCase(prompt="Should I buy a like new or a used phone?", clarification=True),
    ClarificationCase(prompt="A phone for my wife under $300", clarification=False),
    ClarificationCase(prompt="Do you have an iPhone 13 under $300?", clarification=False),
    ClarificationCase(prompt="Android with long battery life", clarification=False),
    ClarificationCase(prompt="Galaxy S25 Ultra like new", clarification=False),
    ClarificationCase(prompt="Pixel under 400 dollars", clarification=False),
    ClarificationCase(prompt="Broken iPhone for parts", clarification=False),
]

# Metrics


def clarification_match(outputs: Outputs, reference_outputs: Outputs) -> dict[str, Any]:
    """A clarification is returned when it is expected, and only then."""
    parsed = outputs.get("parsed")
    if parsed is None:
        return result("clarification", False)
    return result("clarification", (parsed.get("clarification") is not None) == reference_outputs["clarification"])


DATASET = EvalDataset(
    name="rag.clarification",
    examples=[case.example() for case in CASES],
    target=target,
    metrics=[valid_output, clarification_match],
)
