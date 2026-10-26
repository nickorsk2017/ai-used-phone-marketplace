"""Step `rag.parse`: prompt parsing, docs/ai/RAG.md#llm-output-structure, docs/ai/EVALUATION.md#datasets.

Operators follow the parse prompt: "under" is `<=`, "from" is `>=`, a range is `>=` with `max_value`;
"used" is `average`, "for parts" is `for_repair`. An expected field that a case does not set is not checked;
a field set to `None` must be absent in the output.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from core.llm import INVALID_LLM_OUTPUT
from eval.metrics import Outputs, result, valid_output
from eval.schemas import EvalDataset, Example
from modules.rag import services as rag_service
from modules.rag.schemas.search import PhoneCondition, PriceFilter

# Cases


class ParseExpected(BaseModel):
    model_config = ConfigDict(extra="forbid")

    condition: list[PhoneCondition] | None = None
    price: PriceFilter | None = None
    os: Literal["ios", "android"] | None = None


class ParseCase(BaseModel):
    prompt: str = Field(min_length=1)
    expected: ParseExpected

    def example(self) -> Example:
        return Example(
            inputs={"prompt": self.prompt}, outputs=self.expected.model_dump(mode="json", exclude_unset=True)
        )


ANY_PRICE = None
CASES: list[ParseCase] = [
    ParseCase(
        prompt="Android phone under $300",
        expected=ParseExpected(condition=None, price={"operator": "<=", "value": 300}, os="android"),
    ),
    ParseCase(
        prompt="Like new iPhone for 400-600 dollars",
        expected=ParseExpected(
            condition=["like_new"], price={"operator": ">=", "value": 400, "max_value": 600}, os="ios"
        ),
    ),
    ParseCase(
        prompt="Used Samsung under 500 dollars",
        expected=ParseExpected(condition=["average"], price={"operator": "<=", "value": 500}, os="android"),
    ),
    ParseCase(
        prompt="Broken iPhone for parts",
        expected=ParseExpected(condition=["for_repair"], price=ANY_PRICE, os="ios"),
    ),
    ParseCase(
        prompt="Pixel 8 like new",
        expected=ParseExpected(condition=["like_new"], price=ANY_PRICE, os="android"),
    ),
    ParseCase(
        prompt="A phone with a good camera for 200-350 USD",
        expected=ParseExpected(condition=None, price={"operator": ">=", "value": 200, "max_value": 350}),
    ),
    ParseCase(
        prompt="iPhone 13 under $300",
        expected=ParseExpected(condition=None, price={"operator": "<=", "value": 300}, os="ios"),
    ),
    ParseCase(
        prompt="Android with a 5000 mAh battery under 250",
        expected=ParseExpected(condition=None, price={"operator": "<=", "value": 250}, os="android"),
    ),
    ParseCase(
        prompt="Used Galaxy S24 Ultra",
        expected=ParseExpected(condition=["average"], price=ANY_PRICE, os="android"),
    ),
    ParseCase(
        prompt="Like new iPhone from $800",
        expected=ParseExpected(condition=["like_new"], price={"operator": ">=", "value": 800}, os="ios"),
    ),
    ParseCase(
        prompt="Xiaomi or POCO under 350, like new or used",
        expected=ParseExpected(condition=["like_new", "average"], price={"operator": "<=", "value": 350}, os="android"),
    ),
    ParseCase(
        prompt="Android usado hasta 200 dólares",
        expected=ParseExpected(condition=["average"], price={"operator": "<=", "value": 200}, os="android"),
    ),
    ParseCase(
        prompt="A phone for my wife under $300",
        expected=ParseExpected(condition=None, price={"operator": "<=", "value": 300}),
    ),
    ParseCase(
        prompt="Do you have an iPhone 15 Pro?",
        expected=ParseExpected(condition=None, price=ANY_PRICE, os="ios"),
    ),
    ParseCase(
        prompt="Samsung foldable for 900-1200 dollars",
        expected=ParseExpected(condition=None, price={"operator": ">=", "value": 900, "max_value": 1200}, os="android"),
    ),
]

# Target


async def target(inputs: dict[str, Any]) -> dict[str, Any]:
    """`rag.services.parse_prompt`. An invalid output left after the repeat is returned as `error`."""
    try:
        parsed = await rag_service.parse_prompt(inputs["prompt"])
    except INVALID_LLM_OUTPUT as error:
        return {"error": type(error).__name__}
    return {"parsed": parsed.model_dump(mode="json", exclude_none=True)}


# Metrics


def _parsed_field(outputs: Outputs, key: str) -> Any:
    parsed = outputs["parsed"]
    match key:
        case "condition":
            condition = parsed["filters"].get("condition")
            return None if condition is None else sorted(condition["value"])
        case "price":
            price = parsed["filters"].get("price")
            if price is None:
                return None
            return {"operator": price["operator"], "value": price["value"], "max_value": price.get("max_value")}
        case "os":
            os = parsed["preferences"].get("os")
            return None if os is None else os["value"]
    raise ValueError(f"Unknown field {key}")


def _expected_field(reference_outputs: Outputs, key: str) -> Any:
    expected = reference_outputs[key]
    match key:
        case "condition":
            return None if expected is None else sorted(expected)
        case "price":
            return None if expected is None else {**expected, "max_value": expected.get("max_value")}
    return expected


def _field_match(key: str, outputs: Outputs, reference_outputs: Outputs) -> dict[str, Any]:
    if key not in reference_outputs:
        return result(key, None)
    if outputs.get("parsed") is None:
        return result(key, False)
    return result(key, _parsed_field(outputs, key) == _expected_field(reference_outputs, key))


def condition_match(outputs: Outputs, reference_outputs: Outputs) -> dict[str, Any]:
    """Condition filter, compared as a set."""
    return _field_match("condition", outputs, reference_outputs)


def price_match(outputs: Outputs, reference_outputs: Outputs) -> dict[str, Any]:
    """Operator, value and maximum value of the price filter."""
    return _field_match("price", outputs, reference_outputs)


def os_match(outputs: Outputs, reference_outputs: Outputs) -> dict[str, Any]:
    return _field_match("os", outputs, reference_outputs)


DATASET = EvalDataset(
    name="rag.parse",
    examples=[case.example() for case in CASES],
    target=target,
    metrics=[valid_output, condition_match, price_match, os_match],
)
