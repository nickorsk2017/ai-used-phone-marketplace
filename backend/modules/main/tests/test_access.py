"""`Owner` access level: docs/backend/AUTH.md#access."""

import uuid
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI

from modules.main.app import create_app
from modules.main.dependencies import owner_access
from modules.users import services as users_service
from modules.users.schemas import UserRead

VALID_USER = {"whatsapp": "+14155552671", "first_name": "Ann", "last_name": "Lee"}

OwnedProbe = Annotated[
    UserRead,
    Depends(owner_access(users_service.get_user, lambda user: user.id, path_param="resource_id", not_found="Gone")),
]


def probe_app() -> FastAPI:
    app = create_app()

    @app.get("/api/probe/{resource_id}")
    async def probe(resource: OwnedProbe) -> dict[str, str]:
        return {"id": str(resource.id)}

    return app


def client_for(app: FastAPI) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def new_user(client: httpx.AsyncClient) -> str:
    client.cookies.clear()
    return (await client.post("/api/users", json=VALID_USER)).json()["id"]


async def test_owner_gets_the_resource() -> None:
    async with client_for(probe_app()) as client:
        user_id = await new_user(client)
        response = await client.get(f"/api/probe/{user_id}")
    assert response.status_code == 200
    assert response.json() == {"id": user_id}


async def test_owner_check_compares_uuids() -> None:
    async with client_for(probe_app()) as client:
        user_id = await new_user(client)
        assert (await client.get(f"/api/probe/{user_id.upper()}")).status_code == 200


async def test_foreign_resource_is_forbidden() -> None:
    async with client_for(probe_app()) as client:
        owner_id = await new_user(client)
        await new_user(client)
        assert (await client.get(f"/api/probe/{owner_id}")).status_code == 403


async def test_unknown_and_malformed_resource_return_404() -> None:
    async with client_for(probe_app()) as client:
        await new_user(client)
        assert (await client.get(f"/api/probe/{uuid.uuid4()}")).status_code == 404
        assert (await client.get("/api/probe/u-1")).status_code == 404


async def test_owner_endpoint_requires_a_session() -> None:
    async with client_for(probe_app()) as client:
        owner_id = await new_user(client)
        client.cookies.clear()
        assert (await client.get(f"/api/probe/{owner_id}")).status_code == 401
