from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.config import ENV_FILE, settings_errors


class PhonesSettings(BaseSettings):
    """Settings of `modules/phones`: docs/backend/DESIGN.md#configuration."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    openai_api_key: str = Field(min_length=1)
    description_model: str = "gpt-5.6-luna"
    guardrail_model: str = "gpt-5.6-luna"


@lru_cache
def get_settings() -> PhonesSettings:
    return PhonesSettings()


def config_errors() -> list[str]:
    """Missing or invalid settings of `modules/phones`."""
    return settings_errors(get_settings)
