"""LangSmith settings and their export to the process environment: docs/ai/EVALUATION.md#tracing.

LangChain, LangGraph and `langsmith` read the LangSmith settings from the process environment only,
so `configure_tracing` copies them there from `backend/.env` before the first LLM client is created.
"""

import os
from functools import lru_cache

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.config import ENV_FILE, settings_errors

DEFAULT_PROJECT = "second-hand-mobile-e-market"
# Older name of the switch, still read by LangChain: set together so one of them cannot turn tracing on alone.
LEGACY_TRACING_VARIABLE = "LANGCHAIN_TRACING_V2"


class TracingSettings(BaseSettings):
    """LangSmith settings of `core`: docs/backend/DESIGN.md#configuration."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    langsmith_tracing: bool = False
    langsmith_api_key: str = Field(default="", validate_default=True)
    langsmith_project: str = DEFAULT_PROJECT
    langsmith_endpoint: str = ""

    @field_validator("langsmith_api_key")
    @classmethod
    def key_required_with_tracing(cls, value: str, info: ValidationInfo) -> str:
        """Validated after `langsmith_tracing`: the fields are validated in the declaration order."""
        if info.data.get("langsmith_tracing") and not value:
            raise ValueError("required when LANGSMITH_TRACING=true")
        return value


@lru_cache
def get_settings() -> TracingSettings:
    return TracingSettings()


def config_errors() -> list[str]:
    """Missing or invalid LangSmith settings."""
    return settings_errors(get_settings)


def configure_tracing(force: bool = False) -> TracingSettings:
    """Export the settings to the process environment. `force` turns tracing on for `make eval`.

    Raises `ValueError` when tracing is forced without `LANGSMITH_API_KEY`.
    """
    settings = get_settings()
    enabled = settings.langsmith_tracing or force
    if enabled and not settings.langsmith_api_key:
        raise ValueError("LANGSMITH_API_KEY is required for LangSmith tracing and evaluation")
    switch = "true" if enabled else "false"
    os.environ["LANGSMITH_TRACING"] = switch
    os.environ[LEGACY_TRACING_VARIABLE] = switch
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    if settings.langsmith_api_key:
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    if settings.langsmith_endpoint:
        os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint
    return settings
