"""Rate limit of `modules/auth`: docs/INFRA.md#application."""

import httpx
from fastapi import Depends, FastAPI

from modules.main.app import create_app
from modules.main.rate_limit import RateLimit


def client_from(ip: str) -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=create_app(), client=(ip, 12345))
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def test_sixth_auth_request_in_window_is_limited() -> None:
    async with client_from("10.0.0.1") as client:
        for _ in range(5):
            assert (await client.get("/api/users/u-1")).status_code == 401
        response = await client.post("/api/users", json={})
    assert response.status_code == 429
    assert 1 <= int(response.headers["retry-after"]) <= 10


async def test_limit_is_per_client_ip() -> None:
    async with client_from("10.0.0.1") as client:
        for _ in range(5):
            await client.get("/api/users/u-1")
    async with client_from("10.0.0.2") as client:
        assert (await client.get("/api/users/u-1")).status_code == 401


async def test_health_is_not_limited() -> None:
    async with client_from("10.0.0.1") as client:
        for _ in range(5):
            await client.get("/api/users/u-1")
        assert (await client.get("/api/health")).status_code == 200


async def test_window_expires_and_stale_clients_are_swept() -> None:
    now = [0.0]
    limit = RateLimit(limit=2, window_seconds=10, clock=lambda: now[0])
    app = FastAPI()

    @app.get("/limited", dependencies=[Depends(limit)])
    async def limited() -> None:
        return None

    transport = httpx.ASGITransport(app=app, client=("10.0.0.1", 12345))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/limited")).status_code == 200
        now[0] = 4.0
        assert (await client.get("/limited")).status_code == 200
        assert (await client.get("/limited")).status_code == 429
        now[0] = 10.5
        assert (await client.get("/limited")).status_code == 200
        now[0] = 100.0
        assert (await client.get("/limited")).status_code == 200
    assert list(limit._hits) == ["10.0.0.1"]
    assert len(limit._hits["10.0.0.1"]) == 1
