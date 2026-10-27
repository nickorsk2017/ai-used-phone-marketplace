"""Startup configuration check: docs/backend/DESIGN.md#configuration."""

from pathlib import Path

import pytest

from core import config as database_config
from core.config import ENV_FILE as DATABASE_ENV_FILE
from core.config import DatabaseSettings, PytestDatabaseSettings
from core.config import get_settings as get_database_settings
from core.tracing import TracingSettings
from core.tracing import get_settings as get_tracing_settings
from modules.main.app import check_config
from modules.main.config import ENV_FILE as MAIN_ENV_FILE
from modules.main.config import MainSettings
from modules.main.config import get_settings as get_main_settings
from modules.phones.config import PhonesSettings
from modules.phones.config import get_settings as get_phones_settings
from modules.rag.config import RagSettings
from modules.rag.config import get_settings as get_rag_settings

BACKEND_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


@pytest.fixture
def no_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SESSION_SECRET", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    for variable in ("LANGSMITH_TRACING", "LANGSMITH_API_KEY", "LANGSMITH_PROJECT", "LANGSMITH_ENDPOINT"):
        monkeypatch.delenv(variable, raising=False)
    for settings in (DatabaseSettings, TracingSettings, MainSettings, PhonesSettings, RagSettings):
        monkeypatch.setitem(settings.model_config, "env_file", None)
    clear_settings()
    yield
    clear_settings()


def clear_settings() -> None:
    for get_settings in (
        get_database_settings,
        get_tracing_settings,
        get_main_settings,
        get_phones_settings,
        get_rag_settings,
    ):
        get_settings.cache_clear()


VALID_SECRET = "s" * 32
OPENAI_KEY = "test-openai-key"


def test_missing_variables_stop_the_app(no_env: None) -> None:
    with pytest.raises(SystemExit) as exc:
        check_config()
    assert "SESSION_SECRET: Field required" in str(exc.value)
    assert str(exc.value).count("OPENAI_API_KEY: Field required") == 1


def test_short_session_secret_stops_the_app(no_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://postgres@localhost:5432/app")
    monkeypatch.setenv("SESSION_SECRET", VALID_SECRET[:-1])
    monkeypatch.setenv("OPENAI_API_KEY", OPENAI_KEY)
    with pytest.raises(SystemExit) as exc:
        check_config()
    assert "SESSION_SECRET: String should have at least 32 characters" in str(exc.value)


def test_complete_configuration_passes(no_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://postgres@localhost:5432/app")
    monkeypatch.setenv("SESSION_SECRET", VALID_SECRET)
    monkeypatch.setenv("OPENAI_API_KEY", OPENAI_KEY)
    check_config()


def test_cookie_is_secure_by_default(no_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("COOKIE_SECURE", raising=False)
    monkeypatch.setenv("SESSION_SECRET", VALID_SECRET)
    assert MainSettings().cookie_secure is True


def test_ai_models_have_the_documented_defaults(no_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("DESCRIPTION_MODEL", "GUARDRAIL_MODEL", "EMBEDDING_MODEL"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", OPENAI_KEY)
    assert PhonesSettings().description_model == "gpt-5.6-luna"
    assert PhonesSettings().guardrail_model == "gpt-5.6-luna"
    assert RagSettings().embedding_model == "text-embedding-3-small"


def test_database_url_is_built_from_postgres_variables(no_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POSTGRES_USER", "market")
    monkeypatch.setenv("POSTGRES_PASSWORD", "p@ss/word")
    monkeypatch.setenv("POSTGRES_DB", "market_db")
    monkeypatch.setenv("POSTGRES_HOST", "db")
    monkeypatch.setenv("POSTGRES_PORT", "5433")
    assert DatabaseSettings().database_url == "postgresql://market:p%40ss%2Fword@db:5433/market_db"
    assert DatabaseSettings().async_database_url == "postgresql+asyncpg://market:p%40ss%2Fword@db:5433/market_db"


def test_database_url_defaults(no_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB", "POSTGRES_HOST", "POSTGRES_PORT"):
        monkeypatch.delenv(name, raising=False)
    assert DatabaseSettings().database_url == "postgresql://postgres@localhost:5432/app"


def test_test_database_is_built_from_test_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(PytestDatabaseSettings.model_config, "env_file", None)
    monkeypatch.setenv("TEST_DATABASE_USER", "market")
    monkeypatch.setenv("TEST_DATABASE_PASSWORD", "p@ss")
    monkeypatch.setenv("TEST_DATABASE_DB", "market_test")
    monkeypatch.setenv("POSTGRES_HOST", "db")
    monkeypatch.setenv("POSTGRES_PORT", "5433")
    assert database_config.test_database_url() == "postgresql://market:p%40ss@db:5433/market_test"


def test_database_url_from_the_environment_wins(no_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POSTGRES_DB", "market_db")
    monkeypatch.setenv("DATABASE_URL", "postgresql://postgres@localhost:5432/app_test")
    assert DatabaseSettings().database_url == "postgresql://postgres@localhost:5432/app_test"


@pytest.mark.parametrize("env_file", [DATABASE_ENV_FILE, MAIN_ENV_FILE])
def test_settings_read_backend_env_file(env_file: Path) -> None:
    assert env_file == BACKEND_ENV_FILE


def test_env_file_is_read_from_another_directory(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    env_file = tmp_path / "backend.env"
    env_file.write_text("CORS_ORIGINS=https://example.com\n")
    monkeypatch.setitem(MainSettings.model_config, "env_file", env_file)
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    monkeypatch.chdir(tmp_path.parent)
    assert MainSettings().cors_origin_list == ["https://example.com"]
