"""Schemas of the search pipeline: docs/ai/RAG.md, docs/ai/RERANKING.md."""

import uuid
from typing import Annotated, Any, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, StringConstraints, model_validator

PhoneCondition = Literal["like_new", "average", "for_repair"]
PROMPT_MAX_LENGTH = 1000
MODEL_IDS_MAX = 10
# Same format as `phones.model_code`: docs/backend/SCHEMAS.md#phones-modulesphones.
MODEL_CODE_PATTERN = r"^[A-Z0-9-]{2,32}$"
CLARIFICATION_MAX_LENGTH = 300


class PromptBlocked(Exception):
    """Guardrail 2 blocked the search prompt: docs/ai/GUARDRAILS.md#guardrail-2-search-prompt."""


class SearchRequest(BaseModel):
    """Body of `POST /api/search`: docs/backend/API.md#search."""

    model_config = ConfigDict(extra="forbid")

    prompt: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=PROMPT_MAX_LENGTH)]


class SearchGuardrailVerdict(BaseModel):
    """LLM output of Guardrail 2."""

    allowed: bool
    category: Literal["prompt_injection"] | None = None


Operator = Literal["<=", ">=", "<", ">", "="]


class ConditionFilter(BaseModel):
    value: list[PhoneCondition] = Field(min_length=1)


class PriceFilter(BaseModel):
    operator: Operator
    value: int = Field(gt=0)
    # The second bound of a range (`400-600`): `operator` is `>=` and `max_value` is the upper bound.
    max_value: int | None = Field(default=None, gt=0)


class Filters(BaseModel):
    """Set only when the prompt sets them: applied in SQL, docs/ai/RAG.md#llm-output-structure."""

    condition: ConditionFilter | None = None
    price: PriceFilter | None = None


class OsPreference(BaseModel):
    value: Literal["ios", "android"]


class NumberPreference(BaseModel):
    operator: Operator
    value: float = Field(gt=0)


class Preferences(BaseModel):
    os: OsPreference | None = None
    camera_megapixels: NumberPreference | None = None
    battery_capacity: NumberPreference | None = None
    display_size: NumberPreference | None = None


def _normalize_codes(value: Any) -> Any:
    if not isinstance(value, list):
        return value
    codes = [code.strip().upper() for code in value if isinstance(code, str) and code.strip()]
    return list(dict.fromkeys(codes))[:MODEL_IDS_MAX]


ModelCode = Annotated[str, StringConstraints(pattern=MODEL_CODE_PATTERN)]


class ParsedPrompt(BaseModel):
    """LLM output of the prompt parsing: docs/ai/RAG.md#llm-output-structure.

    Either `clarification` (no phone criteria or an advice question, docs/ai/RAG.md#clarification) or the search fields.
    """

    clarification: (
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=CLARIFICATION_MAX_LENGTH)]
        | None
    ) = None
    filters: Filters = Field(default_factory=Filters)
    preferences: Preferences = Field(default_factory=Preferences)
    model_ids: Annotated[list[ModelCode], BeforeValidator(_normalize_codes)] = Field(default_factory=list)
    query_for_embedding: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)] | None = None

    @model_validator(mode="after")
    def _clarification_or_search(self) -> "ParsedPrompt":
        if self.clarification is None and self.query_for_embedding is None:
            raise ValueError("query_for_embedding is required without a clarification")
        return self


Source = Literal["model_code", "vector"]


class Candidate(BaseModel):
    """A listing found by retrieval: the reranker input of docs/ai/RERANKING.md#input."""

    model_config = ConfigDict(from_attributes=True)

    phone_id: uuid.UUID
    model_code: str
    model_name: str
    os: Literal["ios", "android"]
    camera_megapixels: int
    battery_capacity: int
    display_size: float
    description: str
    condition_note: str
    condition: PhoneCondition
    price: int
    source: Source = "model_code"
    distance: float | None = None


class RerankScore(BaseModel):
    # The reranker returns the ID as text: unknown IDs are removed by the validation in code.
    phone_id: str
    relevance: float = Field(ge=0, le=1)


class SearchResult(BaseModel):
    """Result of `search`: the ranked listing IDs or the clarification text, docs/ai/RAG.md#module-interface."""

    phone_ids: list[uuid.UUID] = Field(default_factory=list)
    clarification: str | None = None


class RerankOutput(BaseModel):
    """LLM output of the reranker: docs/ai/RERANKING.md#output."""

    results: list[RerankScore]
