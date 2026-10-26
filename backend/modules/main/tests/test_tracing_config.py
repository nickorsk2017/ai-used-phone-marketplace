"""LangSmith settings: docs/backend/DESIGN.md#configuration, docs/ai/EVALUATION.md#tracing."""

import os
from collections.abc import Iterator

import pytest

import conftest  # noqa: F401  # test environment: no traces, stub keys
from core.tracing import DEFAULT_PROJECT, TracingSettings, config_errors, configure_tracing, get_settings
from modules.main.app import check_config

VARIABLES = (
    "LANGSMITH_TRACING",
    "LANGCHAIN_TRACING_V2",
    "LANGSMITH_API_KEY",
    "LANGSMITH_PROJECT",
    "LANGSMITH_ENDPOINT",
)


@pytest.fixture(autouse=True)
def clean_tracing_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """No `backend/.env` and no LangSmith variables; the process environment is restored after the test."""
    saved = {variable: os.environ.get(variable) for variable in VARIABLES}
    for variable in VARIABLES:
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.setitem(TracingSettings.model_config, "env_file", None)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
    for variable, value in saved.items():
        if value is None:
            os.environ.pop(variable, None)
        else:
            os.environ[variable] = value


def test_tracing_is_off_by_default() -> None:
    settings = configure_tracing()
    assert settings.langsmith_tracing is False
    assert os.environ["LANGSMITH_TRACING"] == "false"
    assert os.environ["LANGCHAIN_TRACING_V2"] == "false"
    assert os.environ["LANGSMITH_PROJECT"] == DEFAULT_PROJECT
    assert "LANGSMITH_ENDPOINT" not in os.environ


def test_settings_are_exported_to_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-key")
    monkeypatch.setenv("LANGSMITH_PROJECT", "sme-test")
    monkeypatch.setenv("LANGSMITH_ENDPOINT", "https://eu.api.smith.langchain.com")
    configure_tracing()
    assert os.environ["LANGSMITH_TRACING"] == "true"
    assert os.environ["LANGCHAIN_TRACING_V2"] == "true"
    assert os.environ["LANGSMITH_API_KEY"] == "ls-key"
    assert os.environ["LANGSMITH_PROJECT"] == "sme-test"
    assert os.environ["LANGSMITH_ENDPOINT"] == "https://eu.api.smith.langchain.com"


def test_tracing_without_key_is_a_configuration_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    assert config_errors() == ["LANGSMITH_API_KEY: Value error, required when LANGSMITH_TRACING=true"]
    with pytest.raises(SystemExit) as exc:
        check_config()
    assert "LANGSMITH_API_KEY: Value error, required when LANGSMITH_TRACING=true" in str(exc.value)


def test_no_key_without_tracing_is_valid() -> None:
    assert config_errors() == []


def test_forced_tracing_needs_the_key() -> None:
    with pytest.raises(ValueError, match="LANGSMITH_API_KEY"):
        configure_tracing(force=True)


def test_forced_tracing_turns_tracing_on(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-key")
    configure_tracing(force=True)
    assert os.environ["LANGSMITH_TRACING"] == "true"
