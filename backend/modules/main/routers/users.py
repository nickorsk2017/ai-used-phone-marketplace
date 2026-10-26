"""`/api/users` endpoints: docs/backend/API.md, session flow: docs/backend/AUTH.md#session-flow."""

from fastapi import APIRouter, Depends, HTTPException, Response, status

from modules.main.dependencies import SESSION_REQUIRED, CurrentUser, DbSession, set_session_cookie
from modules.main.rate_limit import users_rate_limit
from modules.users import services as users_service
from modules.users.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(users_rate_limit)])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(body: UserCreate, session: DbSession, response: Response) -> UserRead:
    user = await users_service.create_user(session, body)
    set_session_cookie(response, user.id)
    return user


@router.get("/me")
async def get_current_user(user: CurrentUser) -> UserRead:
    return user


@router.put("/me")
async def update_current_user(body: UserUpdate, user: CurrentUser, session: DbSession) -> UserRead:
    updated = await users_service.update_user(session, user.id, body)
    if updated is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, SESSION_REQUIRED)
    return updated
