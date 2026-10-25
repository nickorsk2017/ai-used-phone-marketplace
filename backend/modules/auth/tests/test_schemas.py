import pytest
from pydantic import ValidationError

from modules.auth.schemas import UserCreate

VALID_USER = {"whatsapp": "+14155552671", "first_name": "Ann", "last_name": "Lee"}


def test_whatsapp_separators_are_removed() -> None:
    user = UserCreate.model_validate({**VALID_USER, "whatsapp": "+1 (415) 555-26.71"})
    assert user.whatsapp == "+14155552671"


@pytest.mark.parametrize("whatsapp", ["14155552671", "+0123456789", "+12345", "+1234567890123456", "+1415abc2671"])
def test_whatsapp_outside_international_format_is_rejected(whatsapp: str) -> None:
    with pytest.raises(ValidationError):
        UserCreate.model_validate({**VALID_USER, "whatsapp": whatsapp})


def test_names_are_trimmed() -> None:
    user = UserCreate.model_validate({**VALID_USER, "first_name": "  Ann ", "last_name": " Lee  "})
    assert (user.first_name, user.last_name) == ("Ann", "Lee")


@pytest.mark.parametrize("field", ["first_name", "last_name"])
def test_blank_name_is_rejected(field: str) -> None:
    with pytest.raises(ValidationError):
        UserCreate.model_validate({**VALID_USER, field: "   "})


def test_client_cannot_set_id() -> None:
    with pytest.raises(ValidationError):
        UserCreate.model_validate({**VALID_USER, "id": "00000000-0000-0000-0000-000000000001"})
