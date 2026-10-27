import os
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

# `backend/.env`, independent of the current directory: docs/backend/DESIGN.md#configuration.
ENV_FILE = Path(__file__).resolve().parents[1] / ".env"

ASYNC_DRIVER_PREFIX = "postgresql+asyncpg://"


def to_async_url(url: str) -> str:
    """PostgreSQL URLs start with `postgres://` or `postgresql://`, SQLAlchemy needs the asyncpg driver."""
    for prefix in ("postgresql+asyncpg://", "postgresql://", "postgres://"):
        if url.startswith(prefix):
            return ASYNC_DRIVER_PREFIX + url.removeprefix(prefix)
    return url


def postgres_url(user: str, password: str, host: str, port: int, database: str) -> str:
    """Connection URL with the user and the password escaped."""
    url = URL.create("postgresql", username=user, password=password or None, host=host, port=port, database=database)
    return url.render_as_string(hide_password=False)


class DatabaseSettings(BaseSettings):
    """One database for all modules, the connection is built from `POSTGRES_*`: docs/backend/DESIGN.md#configuration."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    postgres_user: str = "postgres"
    postgres_password: str = ""
    postgres_db: str = "app"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    @property
    def database_url(self) -> str:
        """`DATABASE_URL` from the environment switches the process to another database: the tests and `make eval`."""
        override = os.environ.get("DATABASE_URL")
        if override:
            return override
        return postgres_url(
            self.postgres_user, self.postgres_password, self.postgres_host, self.postgres_port, self.postgres_db
        )

    @property
    def async_database_url(self) -> str:
        return to_async_url(self.database_url)


@lru_cache
def get_settings() -> DatabaseSettings:
    return DatabaseSettings()


class PytestDatabaseSettings(BaseSettings):
    """Test database of `make backend-test`, server of `POSTGRES_HOST`: docs/backend/DESIGN.md#configuration."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    test_database_user: str = "postgres"
    test_database_password: str = ""
    test_database_db: str = "app_test"
    postgres_host: str = "localhost"
    postgres_port: int = 5432


def test_database_url() -> str:
    """The test database: never the working database."""
    settings = PytestDatabaseSettings()
    return postgres_url(
        settings.test_database_user,
        settings.test_database_password,
        settings.postgres_host,
        settings.postgres_port,
        settings.test_database_db,
    )


class EvalDatabaseSettings(BaseSettings):
    """Evaluation database of `make eval`, server of `POSTGRES_HOST`: docs/ai/EVALUATION.md#evaluation-database."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    eval_database_user: str = "postgres"
    eval_database_password: str = ""
    eval_database_db: str = "app_eval"
    postgres_host: str = "localhost"
    postgres_port: int = 5432


def eval_database_url() -> str:
    """The evaluation database of `make eval`: never the working or the test database."""
    settings = EvalDatabaseSettings()
    return postgres_url(
        settings.eval_database_user,
        settings.eval_database_password,
        settings.postgres_host,
        settings.postgres_port,
        settings.eval_database_db,
    )


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
