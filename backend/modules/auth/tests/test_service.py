import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth import service
from modules.auth.schemas import UserCreate, UserUpdate

ANN = UserCreate(whatsapp="+14155552671", first_name="Ann", last_name="Lee")
BOB = UserUpdate(whatsapp="+442079460958", first_name="Bob", last_name="Stone")


async def test_create_user_returns_database_generated_fields(session: AsyncSession) -> None:
    user = await service.create_user(session, ANN)
    assert isinstance(user.id, uuid.UUID)
    assert user.id.version == 4
    assert user.created_at.tzinfo is not None
    assert (user.whatsapp, user.first_name, user.last_name) == ("+14155552671", "Ann", "Lee")


async def test_get_user_returns_created_user(session: AsyncSession) -> None:
    created = await service.create_user(session, ANN)
    assert await service.get_user(session, created.id) == created


async def test_get_unknown_user_returns_none(session: AsyncSession) -> None:
    assert await service.get_user(session, uuid.uuid4()) is None


async def test_update_user_replaces_fields(session: AsyncSession) -> None:
    created = await service.create_user(session, ANN)
    updated = await service.update_user(session, created.id, BOB)
    assert updated == created.model_copy(update=BOB.model_dump())
    assert await service.get_user(session, created.id) == updated


async def test_update_unknown_user_returns_none(session: AsyncSession) -> None:
    assert await service.update_user(session, uuid.uuid4(), BOB) is None
