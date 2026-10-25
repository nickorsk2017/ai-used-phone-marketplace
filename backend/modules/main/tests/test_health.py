"""`/api/health`: docs/backend/API.md."""

import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine

import core.database
from core.database import is_database_available


async def test_health_with_database(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_health_without_database(client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    unreachable = create_async_engine("postgresql+asyncpg://postgres@127.0.0.1:1/app")
    monkeypatch.setattr(core.database, "get_engine", lambda: unreachable)
    response = await client.get("/api/health")
    await unreachable.dispose()
    assert response.status_code == 503
    assert response.json() == {"detail": "Database is unavailable"}


async def test_database_check_times_out() -> None:
    assert await is_database_available(timeout_seconds=0) is False
