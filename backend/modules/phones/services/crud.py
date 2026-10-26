"""Database functions of `modules/phones`.

They use the session of the request and never commit: docs/backend/DESIGN.md#database-connection.
They return Pydantic schemas, never ORM objects.
"""

import uuid
from collections.abc import Sequence

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.phones.models import Phone
from modules.phones.schemas import PhoneCreate, PhoneRead


async def create_phone(session: AsyncSession, user_id: uuid.UUID, data: PhoneCreate) -> PhoneRead:
    phone = await session.scalar(insert(Phone).values(user_id=user_id, **data.model_dump()).returning(Phone))
    return PhoneRead.model_validate(phone)


async def get_phone(session: AsyncSession, phone_id: uuid.UUID) -> PhoneRead | None:
    phone = await session.get(Phone, phone_id)
    return PhoneRead.model_validate(phone) if phone else None


async def get_phone_owner_id(session: AsyncSession, phone_id: uuid.UUID) -> uuid.UUID | None:
    """User ID of the listing owner, for `modules/main` only: never returned by Public endpoints."""
    return await session.scalar(select(Phone.user_id).where(Phone.id == phone_id))


async def list_user_phones(session: AsyncSession, user_id: uuid.UUID) -> list[PhoneRead]:
    """Listings of one user, newest first."""
    statement = select(Phone).where(Phone.user_id == user_id).order_by(Phone.created_at.desc(), Phone.id)
    return [PhoneRead.model_validate(phone) for phone in await session.scalars(statement)]


async def get_phones(session: AsyncSession, phone_ids: Sequence[uuid.UUID]) -> list[PhoneRead]:
    """Listings in the order of `phone_ids`, an ID without a listing is skipped: docs/backend/API.md#search."""
    if not phone_ids:
        return []
    rows = await session.scalars(select(Phone).where(Phone.id.in_(list(phone_ids))))
    by_id = {phone.id: phone for phone in rows}
    return [PhoneRead.model_validate(by_id[phone_id]) for phone_id in phone_ids if phone_id in by_id]
