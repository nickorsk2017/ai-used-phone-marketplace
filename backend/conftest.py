"""Shared test fixtures. Tests run against PostgreSQL: `TEST_DATABASE_*`."""

import os
import subprocess
import sys
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from pathlib import Path

import httpx
import pytest
from fastapi import FastAPI
from langsmith import Client
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import test_database_url

TEST_DATABASE_URL = test_database_url()
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["SESSION_SECRET"] = "test-session-secret-" + "x" * 32
# httpx sends `Secure` cookies over HTTPS only, the test client uses `http://test`.
os.environ["COOKIE_SECURE"] = "false"
# The OpenAI clients are replaced by stubs in the tests (`ai_stubs`): no real calls.
os.environ["OPENAI_API_KEY"] = "test-openai-key"
# Tests never send traces to LangSmith: docs/ai/EVALUATION.md#tracing.
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from core.database import get_engine, transaction  # noqa: E402
from modules.main.app import create_app  # noqa: E402
from modules.main.rate_limit import RateLimit  # noqa: E402
from modules.phones.services import ai as phones_ai  # noqa: E402
from modules.rag.services import ai as rag_ai  # noqa: E402

BACKEND_DIR = Path(__file__).parent
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"


def run_alembic(*args: str) -> None:
    subprocess.run([sys.executable, "-m", "alembic", "-c", str(ALEMBIC_INI), *args], cwd=BACKEND_DIR, check=True)


@pytest.fixture(scope="session", autouse=True)
def migrated_database() -> None:
    run_alembic("downgrade", "base")
    run_alembic("upgrade", "head")


@pytest.fixture(scope="session", autouse=True)
async def dispose_engine() -> AsyncIterator[None]:
    yield
    await get_engine().dispose()


@pytest.fixture(autouse=True)
async def clean_users(migrated_database: None) -> None:
    async with get_engine().begin() as connection:
        await connection.execute(text("TRUNCATE users, phones, search_index"))


@pytest.fixture(autouse=True)
def reset_rate_limits() -> None:
    RateLimit.reset_all()


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    """Session in one transaction, as in a request: service tests."""
    async for request_session in transaction():
        yield request_session


@pytest.fixture
def app() -> FastAPI:
    return create_app()


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


EMBEDDING_DIMENSIONS = 1536


class StubChatModel:
    """Replaces a LangChain chat model: returns the queued structured answers or raises the queued errors."""

    def __init__(self, *answers: BaseModel | BaseException) -> None:
        self.answers = list(answers)
        self.calls = 0
        self.schemas: list[type] = []
        self.messages: list = []

    def with_structured_output(self, schema: type) -> "StubChatModel":
        self.schemas.append(schema)
        return self

    async def ainvoke(self, messages: list) -> BaseModel:
        self.calls += 1
        self.messages = messages
        answer = self.answers.pop(0)
        if isinstance(answer, BaseException):
            raise answer
        return answer


class StubEmbeddings:
    """Replaces the LangChain embeddings client. Counts the calls, raises `error` when it is set."""

    def __init__(self, error: BaseException | None = None) -> None:
        self.error = error
        self.calls = 0
        self.texts: list[str] = []

    async def aembed_query(self, text: str) -> list[float]:
        self.calls += 1
        self.texts.append(text)
        if self.error is not None:
            raise self.error
        return [0.01] * EMBEDDING_DIMENSIONS


@dataclass
class AiStubs:
    """The AI clients of `modules/phones` and `modules/rag` used by the code under test. Tests replace the fields."""

    description: StubChatModel = field(default_factory=StubChatModel)
    guardrail: StubChatModel = field(default_factory=StubChatModel)
    embeddings: StubEmbeddings = field(default_factory=StubEmbeddings)
    search_guardrail: StubChatModel = field(default_factory=StubChatModel)
    search_parse: StubChatModel = field(default_factory=StubChatModel)
    rerank: StubChatModel = field(default_factory=StubChatModel)


@pytest.fixture(autouse=True)
def ai_stubs(monkeypatch: pytest.MonkeyPatch) -> AiStubs:
    """Every test runs with stub clients: no real OpenAI calls."""
    stubs = AiStubs()
    monkeypatch.setattr(phones_ai, "get_description_model", lambda: stubs.description)
    monkeypatch.setattr(phones_ai, "get_guardrail_model", lambda: stubs.guardrail)
    monkeypatch.setattr(rag_ai, "get_embeddings", lambda: stubs.embeddings)
    monkeypatch.setattr(rag_ai, "get_guardrail_model", lambda: stubs.search_guardrail)
    monkeypatch.setattr(rag_ai, "get_search_model", lambda: stubs.search_parse)
    monkeypatch.setattr(rag_ai, "get_rerank_model", lambda: stubs.rerank)
    return stubs


class TraceCapture(Client):
    """LangSmith client that keeps the runs in memory instead of sending them: `tracing_context(client=...)`."""

    def __init__(self) -> None:
        super().__init__(api_url="http://localhost:1", api_key="test-langsmith-key", auto_batch_tracing=False)
        self.captured: dict[object, dict] = {}

    def create_run(self, name: str, inputs: dict, run_type: str, **kwargs: object) -> None:
        self.captured[kwargs.get("id")] = {"name": name, "inputs": inputs, **kwargs}

    def update_run(self, run_id: object, **kwargs: object) -> None:
        self.captured.setdefault(run_id, {}).update(kwargs)

    def run(self, name: str) -> dict:
        matches = [run for run in self.captured.values() if run.get("name") == name]
        assert len(matches) == 1, f"one run {name} expected, got {len(matches)}"
        return matches[0]

    def metadata(self, name: str) -> dict:
        return (self.run(name).get("extra") or {}).get("metadata", {})
