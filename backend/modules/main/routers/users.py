"""`/api/users` endpoints: docs/backend/API.md, session flow: docs/backend/AUTH.md#session-flow."""

from fastapi import APIRouter, Depends, HTTPException, status

from modules.auth import service as auth_service
from modules.auth.schemas import UserCreate, UserRead, UserUpdate
from modules.main.dependencies import USER_NOT_FOUND, DbSession, OwnedUser
from modules.main.rate_limit import auth_rate_limit

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(auth_rate_limit)])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(body: UserCreate, session: DbSession) -> UserRead:
    return await auth_service.create_user(session, body)


@router.get("/{user_id}")
async def get_user(user: OwnedUser) -> UserRead:
    return user


@router.put("/{user_id}")
async def update_user(body: UserUpdate, user: OwnedUser, session: DbSession) -> UserRead:
    updated = await auth_service.update_user(session, user.id, body)
    if updated is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, USER_NOT_FOUND)
    return updated
