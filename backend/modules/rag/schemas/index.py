import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict


class IndexedPhone(BaseModel):
    """Listing fields copied to `search_index`: docs/backend/SCHEMAS.md#search_index-modulesrag.

    `modules/main` builds it from the listing of `modules/phones`: `rag` does not import `phones`.
    """

    model_config = ConfigDict(from_attributes=True)

    phone_id: uuid.UUID
    model_code: str
    model_name: str
    os: Literal["ios", "android"]
    camera_megapixels: int
    battery_capacity: int
    display_size: Decimal
    description: str
    condition_note: str
    condition: Literal["like_new", "average", "for_repair"]
    price: int
    updated_at: datetime
