import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from functools import lru_cache

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from core.config import get_settings

HEALTH_TIMEOUT_SECONDS = 2.0

TRANSACTION_ATTEMPTS = 2
# `serialization_failure` and `deadlock_detected`: docs/backend/DESIGN.md#transaction-retry.
TRANSIENT_SQLSTATES = frozenset({"40001", "40P01"})


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


def is_transient_error(error: BaseException) -> bool:
    """A lost connection, a serialization failure or a deadlock: the transaction can run again."""
    if not isinstance(error, DBAPIError):
        return False
    if error.connection_invalidated:
        return True
    original = getattr(error, "orig", None)
    sqlstate = getattr(original, "sqlstate", None) or getattr(original, "pgcode", None)
    return sqlstate in TRANSIENT_SQLSTATES


async def run_in_transaction[Result](
    work: Callable[[AsyncSession], Awaitable[Result]], attempts: int = TRANSACTION_ATTEMPTS
) -> Result:
    """Runs `work` in its own transaction and commits. A transient error repeats the whole attempt.

    The commit is a part of the attempt: docs/backend/DESIGN.md#transaction-retry.
    """
    for attempt in range(1, attempts + 1):
        try:
            async with get_session_factory()() as session, session.begin():
                return await work(session)
        except DBAPIError as error:
            if attempt == attempts or not is_transient_error(error):
                raise
    raise AssertionError("unreachable: the last attempt returns or raises")


async def is_database_available(timeout_seconds: float = HEALTH_TIMEOUT_SECONDS) -> bool:
    """`SELECT 1` within the timeout. Any failure means the database is unavailable."""
    try:
        async with asyncio.timeout(timeout_seconds), get_engine().connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception:
        return False
    return True
