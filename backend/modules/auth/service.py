"""Public interface of `modules/auth`. Other modules call only these functions.

Functions use the session of the request and never commit: the transaction is owned by `modules/main`,
docs/backend/DESIGN.md#database-connection. They return Pydantic schemas, never ORM objects.
"""

import uuid

from sqlalchemy import insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.models import User
from modules.auth.schemas import UserCreate, UserRead, UserUpdate


async def create_user(session: AsyncSession, data: UserCreate) -> UserRead:
    user = await session.scalar(insert(User).values(**data.model_dump()).returning(User))
    return UserRead.model_validate(user)


async def get_user(session: AsyncSession, user_id: uuid.UUID) -> UserRead | None:
    user = await session.get(User, user_id)
    return UserRead.model_validate(user) if user else None


async def update_user(session: AsyncSession, user_id: uuid.UUID, data: UserUpdate) -> UserRead | None:
    """Replaces the user fields. `None` when the user does not exist."""
    statement = update(User).where(User.id == user_id).values(**data.model_dump()).returning(User)
    user = await session.scalar(statement)
    return UserRead.model_validate(user) if user else None
