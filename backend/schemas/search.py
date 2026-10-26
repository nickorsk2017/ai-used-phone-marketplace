from pydantic import BaseModel, Field

from modules.phones.schemas import PhoneRead


class SearchResponse(BaseModel):
    """Response of `POST /api/search`: listings in the rank order, docs/backend/API.md#search.

    `clarification` is present only for a prompt without phone criteria or an advice question, then `results` is empty.
    """

    results: list[PhoneRead]
    clarification: str | None = Field(default=None, exclude_if=lambda value: value is None)
