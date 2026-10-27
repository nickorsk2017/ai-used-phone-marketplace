"""Evaluation database of `rag.search`: docs/ai/EVALUATION.md#evaluation-database. No database connection."""

import os
from pathlib import Path

import pytest

import conftest  # noqa: F401  # test environment: no traces, stub keys
from core.config import DatabaseSettings, EvalDatabaseSettings, PytestDatabaseSettings, eval_database_url, get_settings
from eval import database
from eval.database import WorkingDatabaseError, seed_fingerprint, use_eval_database
from modules.rag.config import RagSettings
from modules.rag.config import get_settings as get_rag_settings

WORKING = "postgresql://postgres@localhost:5432/app"
EVAL = "postgresql://postgres@localhost:5432/app_eval"


@pytest.fixture(autouse=True)
def environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(DatabaseSettings.model_config, "env_file", None)
    monkeypatch.setitem(EvalDatabaseSettings.model_config, "env_file", None)
    monkeypatch.setitem(PytestDatabaseSettings.model_config, "env_file", None)
    for name in (
        "EVAL_DATABASE_USER",
        "EVAL_DATABASE_PASSWORD",
        "TEST_DATABASE_USER",
        "TEST_DATABASE_PASSWORD",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("DATABASE_URL", WORKING)
    monkeypatch.setenv("TEST_DATABASE_DB", "app_test")
    monkeypatch.setenv("EVAL_DATABASE_DB", "app_eval")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


# Guard


def test_default_eval_database(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EVAL_DATABASE_DB")
    assert eval_database_url() == EVAL


def test_eval_database_is_built_from_eval_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EVAL_DATABASE_USER", "market")
    monkeypatch.setenv("EVAL_DATABASE_PASSWORD", "p@ss")
    monkeypatch.setenv("EVAL_DATABASE_DB", "market_eval")
    monkeypatch.setenv("POSTGRES_HOST", "db")
    assert eval_database_url() == "postgresql://market:p%40ss@db:5432/market_eval"


def test_process_is_switched_to_the_eval_database() -> None:
    assert use_eval_database() == EVAL
    assert os.environ["DATABASE_URL"] == EVAL
    assert get_settings().database_url == EVAL


@pytest.mark.parametrize(
    ("variable", "clash"),
    [
        ("POSTGRES_", "app"),
        ("TEST_DATABASE_", "app_test"),
    ],
)
def test_working_and_test_databases_are_refused(monkeypatch: pytest.MonkeyPatch, variable: str, clash: str) -> None:
    monkeypatch.setenv("EVAL_DATABASE_DB", clash)
    with pytest.raises(WorkingDatabaseError, match=variable):
        use_eval_database()
    assert os.environ["DATABASE_URL"] == WORKING


def test_no_working_database_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL")
    assert use_eval_database() == EVAL


# Fingerprint


def test_fingerprint_is_stable_and_well_formed() -> None:
    assert seed_fingerprint() == seed_fingerprint()
    assert database.FINGERPRINT_PATTERN.match(seed_fingerprint())


def test_fingerprint_changes_with_a_listing(monkeypatch: pytest.MonkeyPatch) -> None:
    before = seed_fingerprint()
    first = database.LISTINGS[0]
    changed = first._replace(phone=first.phone.model_copy(update={"price": first.phone.price + 1}))
    monkeypatch.setattr(database, "LISTINGS", [changed, *database.LISTINGS[1:]])
    assert seed_fingerprint() != before


def test_fingerprint_changes_with_the_embedding_model(monkeypatch: pytest.MonkeyPatch) -> None:
    before = seed_fingerprint()
    monkeypatch.setattr(database, "get_rag_settings", lambda: RagSettings(embedding_model="text-embedding-3-large"))
    assert seed_fingerprint() != before
    get_rag_settings.cache_clear()


def test_fingerprint_changes_with_a_migration(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "0001_a.py").write_text("")
    monkeypatch.setattr(database, "MIGRATIONS_DIR", tmp_path)
    before = seed_fingerprint()
    (tmp_path / "0002_b.py").write_text("")
    assert seed_fingerprint() != before


async def test_invalid_fingerprint_is_never_written() -> None:
    with pytest.raises(ValueError):
        await database.write_fingerprint("seed:'; DROP TABLE phones; --")


# Reload decision


class Steps:
    """Stubs of the database steps of `prepare_eval_database`, in call order."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch, loaded: str | None | Exception) -> None:
        self.calls: list[str] = []
        self.written: list[str] = []

        async def ensure_database(url: str) -> None:
            self.calls.append("ensure")

        def migrate(url: str) -> None:
            self.calls.append("migrate")

        async def read_fingerprint() -> str | None:
            self.calls.append("read")
            if isinstance(loaded, Exception):
                raise loaded
            return loaded

        async def load_seed(reset: bool) -> None:
            assert reset
            self.calls.append("seed")

        async def write_fingerprint(fingerprint: str) -> None:
            self.calls.append("write")
            self.written.append(fingerprint)

        for name, stub in {
            "ensure_database": ensure_database,
            "migrate": migrate,
            "read_fingerprint": read_fingerprint,
            "load_seed": load_seed,
            "write_fingerprint": write_fingerprint,
        }.items():
            monkeypatch.setattr(database, name, stub)


async def test_matching_fingerprint_skips_the_seed(monkeypatch: pytest.MonkeyPatch) -> None:
    steps = Steps(monkeypatch, loaded=seed_fingerprint())
    await database.prepare_eval_database()
    assert steps.calls == ["ensure", "migrate", "read"]


@pytest.mark.parametrize("loaded", [None, "seed:" + "0" * 64])
async def test_missing_or_changed_fingerprint_reloads_the_seed(
    monkeypatch: pytest.MonkeyPatch, loaded: str | None
) -> None:
    steps = Steps(monkeypatch, loaded=loaded)
    await database.prepare_eval_database()
    assert steps.calls == ["ensure", "migrate", "read", "seed", "write"]
    assert steps.written == [seed_fingerprint()]


async def test_unreadable_fingerprint_reloads_the_seed(monkeypatch: pytest.MonkeyPatch) -> None:
    steps = Steps(monkeypatch, loaded=RuntimeError("permission denied"))
    await database.prepare_eval_database()
    assert steps.calls == ["ensure", "migrate", "read", "seed", "write"]


async def test_guard_runs_before_any_database_step(monkeypatch: pytest.MonkeyPatch) -> None:
    steps = Steps(monkeypatch, loaded=None)
    monkeypatch.setenv("EVAL_DATABASE_DB", "app_test")
    with pytest.raises(WorkingDatabaseError):
        await database.prepare_eval_database()
    assert steps.calls == []
