"""Alembic environment of the whole Backend: one migration chain, docs/backend/SCHEMAS.md#migrations."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from core.config import get_settings
from modules.auth import models  # noqa: F401  registers the tables in the metadata
from modules.auth.database import AuthBase

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata of every module with tables. A new module adds its Base here.
target_metadata = [AuthBase.metadata]


def run_migrations_offline() -> None:
    context.configure(url=get_settings().async_database_url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_sync_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(get_settings().async_database_url, connect_args={"statement_cache_size": 0})
    async with engine.connect() as connection:
        await connection.run_sync(run_sync_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
