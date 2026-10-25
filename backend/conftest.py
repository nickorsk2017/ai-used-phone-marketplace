"""Shared test fixtures. Tests run against PostgreSQL: `TEST_DATABASE_URL`."""

import os
import subprocess
import sys
from collections.abc import AsyncIterator
from pathlib import Path

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://postgres@localhost:5432/app_test")
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from core.database import get_engine, transaction  # noqa: E402
from modules.main.app import create_app  # noqa: E402
from modules.main.rate_limit import RateLimit  # noqa: E402

BACKEND_DIR = Path(__file__).parent
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"


def run_alembic(*args: str) -> None:
    subprocess.run([sys.executable, "-m", "alembic", "-c", str(ALEMBIC_INI), *args], cwd=BACKEND_DIR, check=True)


@pytest.fixture(scope="session", autouse=True)
def migrated_database() -> None:
    run_alembic("downgrade", "base")
    run_alembic("upgrade", "head")


@pytest.fixture(scope="session", autouse=True)
async def dispose_engine() -> AsyncIterator[None]:
    yield
    await get_engine().dispose()


@pytest.fixture(autouse=True)
async def clean_users(migrated_database: None) -> None:
    async with get_engine().begin() as connection:
        await connection.execute(text("TRUNCATE users"))


@pytest.fixture(autouse=True)
def reset_rate_limits() -> None:
    RateLimit.reset_all()


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    """Session in one transaction, as in a request: service tests."""
    async for request_session in transaction():
        yield request_session


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
