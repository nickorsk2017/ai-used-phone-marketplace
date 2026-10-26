"""Session cookie and access checks of the API: docs/backend/AUTH.md#cookie, docs/backend/AUTH.md#access."""

import uuid
from collections.abc import Awaitable, Callable
from typing import Annotated, Any

from fastapi import Cookie, Depends, HTTPException, Path, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import run_in_transaction, transaction
from modules.auth import services as auth_service
from modules.main.config import get_settings
from modules.users.schemas import UserRead

ACCESS_DENIED = "Access denied"
SESSION_REQUIRED = "Session is required"

SESSION_COOKIE = "session"
SESSION_COOKIE_PATH = "/api"
# 400 days, the browser maximum. The cookie is set again on every request with a valid session.
SESSION_COOKIE_MAX_AGE = 400 * 24 * 60 * 60

# One session and one transaction per request, committed before the response is sent:
# docs/backend/DESIGN.md#database-connection.
DbSession = Annotated[AsyncSession, Depends(transaction, scope="function")]


def _cookie_options() -> dict[str, Any]:
    return {"path": SESSION_COOKIE_PATH, "secure": get_settings().cookie_secure, "httponly": True, "samesite": "lax"}


def set_session_cookie(response: Response, user_id: uuid.UUID) -> None:
    token = auth_service.issue_token(user_id, get_settings().session_secret)
    response.set_cookie(SESSION_COOKIE, token, max_age=SESSION_COOKIE_MAX_AGE, **_cookie_options())


def session_removal_headers() -> dict[str, str]:
    response = Response()
    response.delete_cookie(SESSION_COOKIE, **_cookie_options())
    return {"set-cookie": response.headers["set-cookie"]}


async def get_current_user(
    session: DbSession,
    response: Response,
    token: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
) -> UserRead:
    """Required by the `User` and `Owner` access levels. An invalid session returns 401 and removes the cookie."""
    return _session_user(await auth_service.authenticate(session, token, get_settings().session_secret), response)


async def get_current_user_short_session(
    response: Response,
    token: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
) -> UserRead:
    """`CurrentUser` of endpoints with slow external calls (LLM, embeddings).

    Authenticates in its own short transaction, closed before the endpoint runs, so the request does not hold
    a connection while it waits: docs/backend/DESIGN.md#database-connection.
    """

    async def authenticate(session: AsyncSession) -> UserRead | None:
        return await auth_service.authenticate(session, token, get_settings().session_secret)

    return _session_user(await run_in_transaction(authenticate), response)


def _session_user(user: UserRead | None, response: Response) -> UserRead:
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, SESSION_REQUIRED, headers=session_removal_headers())
    set_session_cookie(response, user.id)
    return user


CurrentUser = Annotated[UserRead, Depends(get_current_user)]
CurrentUserShortSession = Annotated[UserRead, Depends(get_current_user_short_session)]


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
        current_user: CurrentUser,
        resource_id: Annotated[str, Path(alias=path_param)],
    ) -> Any:
        parsed_id = _parse_id(resource_id)
        resource = await load(session, parsed_id) if parsed_id else None
        if resource is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, not_found)
        if not auth_service.is_owner(current_user.id, owner_of(resource)):
            raise HTTPException(status.HTTP_403_FORBIDDEN, ACCESS_DENIED)
        return resource

    return dependency
