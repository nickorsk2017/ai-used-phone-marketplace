"""Evaluation database of `rag.search`: docs/ai/EVALUATION.md#evaluation-database.

Run from `backend/` to prepare it without the evaluation: `python -m eval.database` (`make docker-seed-test`).

A database of its own (`EVAL_DATABASE_*`): not the working database of `POSTGRES_*` and not the test database
of `TEST_DATABASE_*`. The seed is reloaded only when its fingerprint changed.
"""

import asyncio
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import asyncpg
from langsmith import tracing_context
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.engine import make_url

from core.config import eval_database_url, get_settings, test_database_url, to_async_url
from core.database import get_engine, transaction
from modules.rag.config import get_settings as get_rag_settings
from seed.run import LISTINGS
from seed.run import main as load_seed
from seed.users.seed_1 import USERS

BACKEND_DIR = Path(__file__).resolve().parents[1]
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"
MIGRATIONS_DIR = BACKEND_DIR / "migrations" / "versions"
MAINTENANCE_DATABASE = "postgres"
FINGERPRINT_PREFIX = "seed:"
FINGERPRINT_PATTERN = re.compile(r"^seed:[0-9a-f]{64}$")


class WorkingDatabaseError(RuntimeError):
    """`EVAL_DATABASE_*` points to the working database or to the test database."""


# Guard


def _working_database_url() -> str | None:
    """`DATABASE_URL` from the environment or `backend/.env`; `None` when it is not set, for example in CI."""
    try:
        return get_settings().async_database_url
    except ValidationError:
        return None


def use_eval_database() -> str:
    """Point `DATABASE_URL` of this process to the evaluation database, before the first engine is created."""
    url = eval_database_url()
    clashes = {"POSTGRES_*": _working_database_url(), "TEST_DATABASE_*": to_async_url(test_database_url())}
    for variable, other in clashes.items():
        if other is not None and to_async_url(url) == other:
            raise WorkingDatabaseError(
                f"EVAL_DATABASE_* is the database of {variable}: the seed reload would change it"
            )
    os.environ["DATABASE_URL"] = url
    get_settings.cache_clear()
    return url


# Database and migrations


async def ensure_database(url: str) -> None:
    """Create the evaluation database when it does not exist, through the maintenance database of the server."""
    target = make_url(url)
    maintenance = target.set(drivername="postgresql", database=MAINTENANCE_DATABASE)
    connection = await asyncpg.connect(maintenance.render_as_string(hide_password=False))
    try:
        exists = await connection.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", target.database)
        if not exists:
            name = target.database.replace('"', '""')
            await connection.execute(f'CREATE DATABASE "{name}"')
            print(f"Created the evaluation database {target.database}.")
    finally:
        await connection.close()


def migrate(url: str) -> None:
    subprocess.run(
        [sys.executable, "-m", "alembic", "-c", str(ALEMBIC_INI), "upgrade", "head"],
        cwd=BACKEND_DIR,
        env={**os.environ, "DATABASE_URL": url},
        check=True,
    )


# Seed fingerprint


def seed_fingerprint() -> str:
    """Hash of the seed users and listings, the embedding model and the migration files."""
    content = {
        "users": [user.model_dump(mode="json") for user in USERS],
        "listings": [{"user": item.user, "phone": item.phone.model_dump(mode="json")} for item in LISTINGS],
        "embedding_model": get_rag_settings().embedding_model,
        "migrations": sorted(path.name for path in MIGRATIONS_DIR.glob("*.py")),
    }
    digest = hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
    return FINGERPRINT_PREFIX + digest


async def read_fingerprint() -> str | None:
    async for session in transaction():
        return await session.scalar(
            text("SELECT shobj_description(oid, 'pg_database') FROM pg_database WHERE datname = current_database()")
        )
    return None


async def write_fingerprint(fingerprint: str) -> None:
    """`COMMENT ON` takes no bind parameters: the value is checked against the fingerprint format first."""
    if not FINGERPRINT_PATTERN.match(fingerprint):
        raise ValueError(f"Invalid seed fingerprint {fingerprint!r}")
    async for session in transaction():
        name = (await session.scalar(text("SELECT current_database()"))).replace('"', '""')
        await session.execute(text(f"COMMENT ON DATABASE \"{name}\" IS '{fingerprint}'"))


# Preparation


async def prepare_eval_database() -> None:
    """Guard, database, migrations, then the seed reload when the fingerprint changed."""
    url = use_eval_database()
    await ensure_database(url)
    migrate(url)
    expected = seed_fingerprint()
    try:
        loaded = await read_fingerprint()
    except Exception as error:
        print(f"Could not read the seed fingerprint ({type(error).__name__}): the seed is reloaded.")
        loaded = None
    if loaded == expected:
        print("Evaluation seed is up to date.")
        return
    with tracing_context(enabled=False):
        await load_seed(reset=True)
    try:
        await write_fingerprint(expected)
    except Exception as error:
        print(f"Could not store the seed fingerprint ({type(error).__name__}): the next run reloads the seed.")


async def main() -> None:
    try:
        await prepare_eval_database()
    finally:
        await get_engine().dispose()


if __name__ == "__main__":
    asyncio.run(main())
