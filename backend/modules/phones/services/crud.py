"""Database functions of `modules/phones`.

They use the session of the request and never commit: docs/backend/DESIGN.md#database-connection.
They return Pydantic schemas, never ORM objects.
"""

import uuid

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.phones.models import Phone
from modules.phones.schemas import PhoneCreate, PhoneRead


async def create_phone(session: AsyncSession, user_id: uuid.UUID, data: PhoneCreate) -> PhoneRead:
    phone = await session.scalar(insert(Phone).values(user_id=user_id, **data.model_dump()).returning(Phone))
    return PhoneRead.model_validate(phone)


async def list_user_phones(session: AsyncSession, user_id: uuid.UUID) -> list[PhoneRead]:
    """Listings of one user, newest first."""
    statement = select(Phone).where(Phone.user_id == user_id).order_by(Phone.created_at.desc(), Phone.id)
    return [PhoneRead.model_validate(phone) for phone in await session.scalars(statement)]
