import uuid
from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, PlainSerializer, PositiveInt, StringConstraints

from modules.phones.models.phone import MODEL_CODE_MAX_LENGTH, MODEL_NAME_MAX_LENGTH

PhoneOs = Literal["ios", "android"]
PhoneCondition = Literal["like_new", "average", "for_repair"]

ModelName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MODEL_NAME_MAX_LENGTH)]
# Format of the US model code: docs/backend/SCHEMAS.md#phones-modulesphones.
MODEL_CODE_PATTERN = r"^[A-Z0-9-]{2,32}$"


def normalize_model_code(value: Any) -> Any:
    return value.strip().upper() if isinstance(value, str) else value


ModelCode = Annotated[
    str,
    BeforeValidator(normalize_model_code),
    StringConstraints(pattern=MODEL_CODE_PATTERN, max_length=MODEL_CODE_MAX_LENGTH),
]
ListingText = Annotated[str, StringConstraints(strip_whitespace=True)]
# Inches, `Numeric(4, 2)` in the table, a JSON number in the API.
DisplaySize = Annotated[float, Field(gt=0, lt=100), PlainSerializer(lambda value: round(float(value), 2))]


class PhoneDescriptionRequest(BaseModel):
    """Body of `POST /api/phones/description`."""

    model_config = ConfigDict(extra="forbid")

    model_name: ModelName


class PhoneDescription(BaseModel):
    """Description and model data: docs/features/MY_LISTING.md#description-response."""

    model_code: ModelCode
    model_name: ModelName
    os: PhoneOs
    camera_megapixels: PositiveInt
    battery_capacity: PositiveInt
    display_size: DisplaySize
    description: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class PhoneCreate(PhoneDescription):
    """Body of `POST /api/phones`: the reviewed description plus the listing fields set by the seller.

    Extra fields are rejected: the client cannot set `id`, `user_id` or the dates.
    """

    model_config = ConfigDict(extra="forbid")

    condition: PhoneCondition
    condition_note: ListingText
    price: PositiveInt


class PhoneRead(BaseModel):
    """A listing of its owner. Public endpoints never return `user_id`: docs/backend/AUTH.md#access."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    model_code: str
    model_name: str
    os: PhoneOs
    camera_megapixels: int
    battery_capacity: int
    display_size: DisplaySize
    description: str
    condition: PhoneCondition
    condition_note: str
    price: int
    created_at: datetime
    updated_at: datetime


class MyListings(BaseModel):
    """Response of `GET /api/my-listings`, newest first."""

    listings: list[PhoneRead]


class GuardrailVerdict(BaseModel):
    """LLM Guardrail output: docs/ai/GUARDRAILS.md#guardrail-1-phone-saving."""

    allowed: bool
    category: Literal["toxic", "fraud", "prompt_injection"] | None = None


class GeneratedDescription(BaseModel):
    """Structured LLM output of the description generation: docs/features/MY_LISTING.md#description-response."""

    model_found: bool
    model_code: str | None = None
    model_name: str | None = None
    os: PhoneOs | None = None
    camera_megapixels: int | None = None
    battery_capacity: int | None = None
    display_size: float | None = None
    description: str | None = None
