import re
import uuid
from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict, StringConstraints

from modules.users.models.user import NAME_MAX_LENGTH

# International format `+<7-15 digits>`, same rule as frontend/schemas/myListingsFormSchemas.ts.
WHATSAPP_PATTERN = r"^\+[1-9]\d{6,14}$"
WHATSAPP_SEPARATORS = re.compile(r"[\s().-]")


def normalize_whatsapp(value: Any) -> Any:
    return WHATSAPP_SEPARATORS.sub("", value) if isinstance(value, str) else value


WhatsApp = Annotated[str, BeforeValidator(normalize_whatsapp), StringConstraints(pattern=WHATSAPP_PATTERN)]
PersonName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=NAME_MAX_LENGTH)]


class UserFields(BaseModel):
    """Fields set by the user. Extra fields are rejected: the client cannot set `id` or `created_at`."""

    model_config = ConfigDict(extra="forbid")

    whatsapp: WhatsApp
    first_name: PersonName
    last_name: PersonName


class UserCreate(UserFields):
    """Body of `POST /api/users`."""


class UserUpdate(UserFields):
    """Body of `PUT /api/users/me`: all fields are replaced."""


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    whatsapp: str
    first_name: str
    last_name: str
    created_at: datetime
