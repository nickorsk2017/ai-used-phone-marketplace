"""Authentication and owner check of `modules/auth`.

Functions that read the database use the session of the request and never commit:
docs/backend/DESIGN.md#database-connection.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.services.token import verify_token
from modules.users import services as users_service
from modules.users.schemas import UserRead


async def authenticate(session: AsyncSession, token: str | None, secret: str) -> UserRead | None:
    """The current user of a token: a valid signature and an existing user."""
    user_id = verify_token(token, secret)
    return await users_service.get_user(session, user_id) if user_id else None


def is_owner(user_id: uuid.UUID, owner_id: uuid.UUID) -> bool:
    return user_id == owner_id
