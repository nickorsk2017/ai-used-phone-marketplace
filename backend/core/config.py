from functools import lru_cache
from pathlib import Path

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

# `backend/.env`, independent of the current directory: docs/backend/DESIGN.md#configuration.
ENV_FILE = Path(__file__).resolve().parents[1] / ".env"

ASYNC_DRIVER_PREFIX = "postgresql+asyncpg://"


def to_async_url(url: str) -> str:
    """Supabase gives `postgres://` or `postgresql://` URLs, SQLAlchemy needs the asyncpg driver."""
    for prefix in ("postgresql+asyncpg://", "postgresql://", "postgres://"):
        if url.startswith(prefix):
            return ASYNC_DRIVER_PREFIX + url.removeprefix(prefix)
    return url


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


def config_errors() -> list[str]:
    """Missing or invalid database settings, one line per variable. Empty when the settings are valid."""
    try:
        get_settings()
    except ValidationError as exc:
        return [f"{str(error['loc'][0]).upper() if error['loc'] else '?'}: {error['msg']}" for error in exc.errors()]
    return []
