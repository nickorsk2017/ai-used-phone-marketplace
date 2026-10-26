from functools import lru_cache
from pathlib import Path

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

# `backend/.env`, independent of the current directory: docs/backend/DESIGN.md#configuration.
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

SESSION_SECRET_MIN_LENGTH = 32


class MainSettings(BaseSettings):
    """Settings of `modules/main`."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    # Comma-separated origins of the Frontend allowed by CORS.
    cors_origins: str = "http://localhost:3000"
    # Secret of the session token, passed to `modules/auth`: docs/backend/AUTH.md#session-token.
    session_secret: str = Field(min_length=SESSION_SECRET_MIN_LENGTH)
    # `Secure` attribute of the session cookie: docs/backend/AUTH.md#cookie.
    cookie_secure: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> MainSettings:
    return MainSettings()


def config_errors() -> list[str]:
    """Missing or invalid settings of `modules/main`, one line per variable."""
    try:
        get_settings()
    except ValidationError as exc:
        return [f"{str(error['loc'][0]).upper() if error['loc'] else '?'}: {error['msg']}" for error in exc.errors()]
    return []
