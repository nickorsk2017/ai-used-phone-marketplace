import asyncio
from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from core.config import get_settings

HEALTH_TIMEOUT_SECONDS = 2.0


@lru_cache
def get_engine() -> AsyncEngine:
    """One engine and one connection pool for all modules."""
    # The Supabase pooler runs in transaction mode: asyncpg prepared statements must be disabled.
    return create_async_engine(
        get_settings().async_database_url,
        pool_pre_ping=True,
        connect_args={"statement_cache_size": 0},
    )


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def transaction() -> AsyncIterator[AsyncSession]:
    """Session of one request in one transaction: commit on success, rollback on an error.

    Shared by all modules of the request: docs/backend/DESIGN.md#database-connection.
    """
    async with get_session_factory()() as session, session.begin():
        yield session


async def is_database_available(timeout_seconds: float = HEALTH_TIMEOUT_SECONDS) -> bool:
    """`SELECT 1` within the timeout. Any failure means the database is unavailable."""
    try:
        async with asyncio.timeout(timeout_seconds), get_engine().connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception:
        return False
    return True
