"""Access checks of the API: docs/backend/AUTH.md#access."""

import uuid
from collections.abc import Awaitable, Callable
from typing import Annotated, Any

from fastapi import Depends, Header, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import transaction
from modules.auth import service as auth_service
from modules.auth.schemas import UserRead

ACCESS_DENIED = "Access denied"
USER_NOT_FOUND = "User not found"

# One session and one transaction per request, committed before the response is sent:
# docs/backend/DESIGN.md#database-connection.
DbSession = Annotated[AsyncSession, Depends(transaction, scope="function")]


async def get_current_user_id(x_user_id: Annotated[str | None, Header()] = None) -> str:
    """`X-User-Id` works as a bearer token. Required by the `User` and `Owner` access levels."""
    if not x_user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "X-User-Id header is required")
    return x_user_id


CurrentUserId = Annotated[str, Depends(get_current_user_id)]


def _parse_id(value: str) -> uuid.UUID | None:
    try:
        return uuid.UUID(value)
    except ValueError:
        return None


def owner_access[Resource](
    load: Callable[[AsyncSession, uuid.UUID], Awaitable[Resource | None]],
    owner_of: Callable[[Resource], uuid.UUID],
    path_param: str,
    not_found: str,
) -> Callable[..., Awaitable[Resource]]:
    """Dependency of an `Owner` endpoint: loads the resource of `{path_param}` and returns it to its owner only."""

    async def dependency(
        session: DbSession,
        current_user_id: CurrentUserId,
        resource_id: Annotated[str, Path(alias=path_param)],
    ) -> Any:
        parsed_id = _parse_id(resource_id)
        resource = await load(session, parsed_id) if parsed_id else None
        if resource is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, not_found)
        if _parse_id(current_user_id) != owner_of(resource):
            raise HTTPException(status.HTTP_403_FORBIDDEN, ACCESS_DENIED)
        return resource

    return dependency


# A user is the owner of itself.
OwnedUser = Annotated[
    UserRead,
    Depends(owner_access(auth_service.get_user, lambda user: user.id, path_param="user_id", not_found=USER_NOT_FOUND)),
]
