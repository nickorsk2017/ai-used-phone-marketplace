import os
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

# `backend/.env`, independent of the current directory: docs/backend/DESIGN.md#configuration.
ENV_FILE = Path(__file__).resolve().parents[1] / ".env"

ASYNC_DRIVER_PREFIX = "postgresql+asyncpg://"

# Tests and `make eval`: docs/backend/DESIGN.md#configuration. Read from the environment only, never from `.env`.
TEST_DATABASE_URL_DEFAULT = "postgresql://postgres@localhost:5432/app_test"
EVAL_DATABASE_URL_DEFAULT = "postgresql://postgres@localhost:5432/app_eval"


def to_async_url(url: str) -> str:
    """Supabase gives `postgres://` or `postgresql://` URLs, SQLAlchemy needs the asyncpg driver."""
    for prefix in ("postgresql+asyncpg://", "postgresql://", "postgres://"):
        if url.startswith(prefix):
            return ASYNC_DRIVER_PREFIX + url.removeprefix(prefix)
    return url


def test_database_url() -> str:
    """The test database: never the database of `DATABASE_URL`."""
    return os.environ.get("TEST_DATABASE_URL", TEST_DATABASE_URL_DEFAULT)


def eval_database_url() -> str:
    """The evaluation database of `make eval`: never the working or the test database."""
    return os.environ.get("EVAL_DATABASE_URL", EVAL_DATABASE_URL_DEFAULT)


class DatabaseSettings(BaseSettings):
    """One database for all modules."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    database_url: str

    @property
    def async_database_url(self) -> str:
        return to_async_url(self.database_url)


@lru_cache
def get_settings() -> DatabaseSettings:
    return DatabaseSettings()


def settings_errors(load: Callable[[], object]) -> list[str]:
    """Missing or invalid settings of `load`, one line per variable. Empty when the settings are valid."""
    try:
        load()
    except ValidationError as exc:
        return [f"{str(error['loc'][0]).upper() if error['loc'] else '?'}: {error['msg']}" for error in exc.errors()]
    return []


def config_errors() -> list[str]:
    """Missing or invalid database settings."""
    return settings_errors(get_settings)
