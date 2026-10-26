"""Session token and the owner check: docs/backend/AUTH.md#session-token."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth import services as auth_service
from modules.users import services as users_service
from modules.users.schemas import UserCreate

SECRET = "s" * 32
OTHER_SECRET = "o" * 32
ANN = UserCreate(whatsapp="+14155552671", first_name="Ann", last_name="Lee")


def test_issued_token_is_verified() -> None:
    user_id = uuid.uuid4()
    token = auth_service.issue_token(user_id, SECRET)
    assert token.startswith(f"{user_id}.")
    assert auth_service.verify_token(token, SECRET) == user_id


def test_token_of_another_secret_is_rejected() -> None:
    token = auth_service.issue_token(uuid.uuid4(), OTHER_SECRET)
    assert auth_service.verify_token(token, SECRET) is None


def test_token_with_a_replaced_user_id_is_rejected() -> None:
    signature = auth_service.issue_token(uuid.uuid4(), SECRET).split(".", 1)[1]
    assert auth_service.verify_token(f"{uuid.uuid4()}.{signature}", SECRET) is None


@pytest.mark.parametrize("token", [None, "", "no-separator", ".", "abc.def", "not-a-uuid.sig"])
def test_malformed_token_is_rejected(token: str | None) -> None:
    assert auth_service.verify_token(token, SECRET) is None


def test_token_signed_for_a_malformed_id_is_rejected() -> None:
    token = auth_service.issue_token("not-a-uuid", SECRET)  # type: ignore[arg-type]
    assert auth_service.verify_token(token, SECRET) is None


def test_owner_check() -> None:
    user_id = uuid.uuid4()
    assert auth_service.is_owner(user_id, uuid.UUID(str(user_id)))
    assert not auth_service.is_owner(user_id, uuid.uuid4())


async def test_authenticate_returns_the_existing_user(session: AsyncSession) -> None:
    user = await users_service.create_user(session, ANN)
    token = auth_service.issue_token(user.id, SECRET)
    assert await auth_service.authenticate(session, token, SECRET) == user


async def test_authenticate_rejects_an_unknown_user(session: AsyncSession) -> None:
    token = auth_service.issue_token(uuid.uuid4(), SECRET)
    assert await auth_service.authenticate(session, token, SECRET) is None


async def test_authenticate_rejects_an_invalid_token(session: AsyncSession) -> None:
    await users_service.create_user(session, ANN)
    assert await auth_service.authenticate(session, "bad", SECRET) is None
