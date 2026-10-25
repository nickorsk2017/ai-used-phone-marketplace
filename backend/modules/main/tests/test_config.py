"""Startup configuration check: docs/backend/DESIGN.md#configuration."""

from pathlib import Path

import pytest

from core.config import ENV_FILE as DATABASE_ENV_FILE
from core.config import DatabaseSettings
from core.config import get_settings as get_database_settings
from modules.main.app import check_config
from modules.main.config import ENV_FILE as MAIN_ENV_FILE
from modules.main.config import MainSettings
from modules.main.config import get_settings as get_main_settings

BACKEND_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


@pytest.fixture
def no_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setitem(DatabaseSettings.model_config, "env_file", None)
    monkeypatch.setitem(MainSettings.model_config, "env_file", None)
    get_database_settings.cache_clear()
    get_main_settings.cache_clear()
    yield
    get_database_settings.cache_clear()
    get_main_settings.cache_clear()


def test_missing_database_url_stops_the_app(no_env: None) -> None:
    with pytest.raises(SystemExit) as exc:
        check_config()
    assert "DATABASE_URL: Field required" in str(exc.value)


def test_database_url_passes(no_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://postgres@localhost:5432/app")
    check_config()


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
