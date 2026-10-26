from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.config import ENV_FILE, settings_errors


class RagSettings(BaseSettings):
    """Settings of `modules/rag`: docs/backend/DESIGN.md#configuration."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    openai_api_key: str = Field(min_length=1)
    embedding_model: str = "text-embedding-3-small"
    search_model: str = "gpt-5.6-luna"
    rerank_model: str = "gpt-5.6-luna"
    guardrail_model: str = "gpt-5.6-luna"
    rerank_threshold: float = Field(default=0.3, ge=0, le=1)


@lru_cache
def get_settings() -> RagSettings:
    return RagSettings()


def config_errors() -> list[str]:
    """Missing or invalid settings of `modules/rag`."""
    return settings_errors(get_settings)
