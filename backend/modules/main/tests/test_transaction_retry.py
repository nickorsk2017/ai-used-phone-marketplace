"""`run_in_transaction`: docs/backend/DESIGN.md#transaction-retry."""

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import is_transient_error, run_in_transaction
from modules.users.models import User


def raise_sqlstate(sqlstate: str):
    return text(f"DO $$ BEGIN RAISE EXCEPTION 'test error' USING ERRCODE = '{sqlstate}'; END $$")


async def insert_user(session: AsyncSession) -> None:
    await session.execute(text("INSERT INTO users (whatsapp, first_name, last_name) VALUES ('+14155552671', 'A', 'B')"))


async def count_users(session: AsyncSession) -> int:
    return await session.scalar(select(func.count()).select_from(User))


def failing_work(failures: int, sqlstate: str):
    attempts = []

    async def work(session: AsyncSession) -> int:
        attempts.append(1)
        await insert_user(session)
        if len(attempts) <= failures:
            await session.execute(raise_sqlstate(sqlstate))
        return len(attempts)

    return work, attempts


@pytest.mark.parametrize("sqlstate", ["40001", "40P01"])
async def test_transient_error_is_retried_once(sqlstate: str, session: AsyncSession) -> None:
    work, attempts = failing_work(failures=1, sqlstate=sqlstate)
    assert await run_in_transaction(work) == 2
    assert len(attempts) == 2
    assert await count_users(session) == 1


async def test_transient_error_twice_raises_and_saves_nothing(session: AsyncSession) -> None:
    work, attempts = failing_work(failures=2, sqlstate="40001")
    with pytest.raises(DBAPIError):
        await run_in_transaction(work)
    assert len(attempts) == 2
    assert await count_users(session) == 0


async def test_non_transient_error_is_not_retried(session: AsyncSession) -> None:
    work, attempts = failing_work(failures=1, sqlstate="22000")
    with pytest.raises(DBAPIError) as exc:
        await run_in_transaction(work)
    assert not is_transient_error(exc.value)
    assert len(attempts) == 1
    assert await count_users(session) == 0


async def test_other_exceptions_are_not_retried() -> None:
    attempts = []

    async def work(session: AsyncSession) -> None:
        attempts.append(1)
        raise ValueError("domain error")

    with pytest.raises(ValueError):
        await run_in_transaction(work)
    assert len(attempts) == 1


def test_lost_connection_is_transient() -> None:
    error = DBAPIError("SELECT 1", {}, Exception("connection lost"), connection_invalidated=True)
    assert is_transient_error(error)
