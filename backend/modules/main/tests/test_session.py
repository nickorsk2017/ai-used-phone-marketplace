"""One session and one transaction per request: docs/backend/DESIGN.md#database-connection."""

from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session_factory
from modules.auth import service as auth_service
from modules.auth.models import User
from modules.auth.schemas import UserCreate, UserRead
from modules.main.app import create_app
from modules.main.dependencies import DbSession, owner_access

ANN = UserCreate(whatsapp="+14155552671", first_name="Ann", last_name="Lee")


def client_for(app: FastAPI) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def count_users() -> int:
    async with get_session_factory()() as session:
        return await session.scalar(select(func.count()).select_from(User))


async def test_owner_dependency_and_endpoint_share_the_session() -> None:
    sessions: list[AsyncSession] = []

    async def load(session: AsyncSession, user_id) -> UserRead | None:
        sessions.append(session)
        return await auth_service.get_user(session, user_id)

    owned = Annotated[UserRead, Depends(owner_access(load, lambda user: user.id, path_param="user_id", not_found="x"))]
    app = create_app()

    @app.get("/probe/{user_id}")
    async def probe(user: owned, session: DbSession) -> dict[str, str]:
        sessions.append(session)
        return {"id": str(user.id)}

    async with client_for(app) as client:
        user = (await client.post("/api/users", json=ANN.model_dump())).json()
        response = await client.get(f"/probe/{user['id']}", headers={"X-User-Id": user["id"]})
    assert response.status_code == 200
    assert len(sessions) == 2
    assert sessions[0] is sessions[1]


async def test_error_after_a_write_rolls_the_request_back() -> None:
    app = create_app()

    @app.post("/probe/fail")
    async def fail(session: DbSession) -> None:
        await auth_service.create_user(session, ANN)
        raise HTTPException(status.HTTP_409_CONFLICT, "Conflict")

    async with client_for(app) as client:
        response = await client.post("/probe/fail")
    assert response.status_code == 409
    assert await count_users() == 0


async def test_successful_request_is_committed(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/users", json=ANN.model_dump())
    assert response.status_code == 201
    assert await count_users() == 1
