"""LangSmith runs of `modules/rag` and `parse_prompt`: docs/ai/EVALUATION.md#tracing, docs/ai/RAG.md#module-interface.

Runs are captured, never sent. No database: the search ends with a clarification after the `parse` node.
"""

import uuid

import pytest
from langsmith import traceable, tracing_context
from pydantic import ValidationError

from conftest import StubChatModel, StubEmbeddings, TraceCapture
from modules.rag import services as rag_service
from modules.rag.schemas.search import Candidate, ParsedPrompt, SearchGuardrailVerdict
from modules.rag.services import ai as rag_ai
from modules.rag.services import graph

CLARIFICATION = ParsedPrompt(clarification="What is your budget?")
SEARCH = ParsedPrompt(filters={"price": {"operator": "<=", "value": 300}}, query_for_embedding="Android phone")
SESSION = object()


def candidate() -> Candidate:
    return Candidate(
        phone_id=uuid.uuid4(),
        model_code="A2483",
        model_name="iPhone 13 Pro",
        os="ios",
        camera_megapixels=12,
        battery_capacity=3095,
        display_size=6.1,
        description="",
        condition_note="",
        condition="average",
        price=300,
    )


async def test_search_is_the_root_run_with_one_span_per_node(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rag_ai, "get_guardrail_model", lambda: StubChatModel(SearchGuardrailVerdict(allowed=True)))
    monkeypatch.setattr(rag_ai, "get_search_model", lambda: StubChatModel(CLARIFICATION))
    capture = TraceCapture()
    with tracing_context(enabled=True, client=capture):
        result = await rag_service.search(SESSION, "I need a phone")
    assert result.clarification == "What is your budget?"
    root = capture.run(graph.SEARCH_RUN_NAME)
    assert root["tags"] == ["rag"]
    assert root.get("parent_run_id") is None
    for node in ("guardrail", "parse"):
        assert capture.run(node)["parent_run_id"] == root["id"]


async def test_session_is_not_in_the_trace_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rag_ai, "get_guardrail_model", lambda: StubChatModel(SearchGuardrailVerdict(allowed=True)))
    monkeypatch.setattr(rag_ai, "get_search_model", lambda: StubChatModel(CLARIFICATION))
    capture = TraceCapture()
    with tracing_context(enabled=True, client=capture):
        await rag_service.search(SESSION, "I need a phone")
    assert capture.captured
    for run in capture.captured.values():
        metadata = (run.get("extra") or {}).get("metadata", {})
        assert "session" not in metadata
        assert SESSION not in metadata.values()


async def test_rerank_fallback_marks_the_rerank_span(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rag_ai, "get_rerank_model", lambda: StubChatModel(RuntimeError("provider down")))
    rerank_span = traceable(name="rerank")(graph.rerank)
    capture = TraceCapture()
    with tracing_context(enabled=True, client=capture):
        state = await rerank_span({"candidates": [candidate()], "parsed": SEARCH})
    assert len(state["result"]) == 1
    metadata = capture.metadata("rerank")
    assert metadata["rerank_fallback"] is True
    assert metadata["rerank_error"] == "RuntimeError"


async def test_rerank_fallback_without_tracing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rag_ai, "get_rerank_model", lambda: StubChatModel(RuntimeError("provider down")))
    state = await graph.rerank({"candidates": [candidate()], "parsed": SEARCH})
    assert len(state["result"]) == 1


async def test_embed_listing_is_the_root_run_rag_embed_listing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rag_ai, "get_embeddings", lambda: StubEmbeddings())
    capture = TraceCapture()
    with tracing_context(enabled=True, client=capture):
        await rag_service.embed_listing("Pixel 8", "Google phone", "Like new")
    assert capture.run("rag.embed_listing")["tags"] == ["rag"]


async def test_parse_prompt_returns_the_parsed_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    model = StubChatModel(SEARCH)
    monkeypatch.setattr(rag_ai, "get_search_model", lambda: model)
    capture = TraceCapture()
    with tracing_context(enabled=True, client=capture):
        parsed = await rag_service.parse_prompt("Android under $300")
    assert parsed == SEARCH
    assert model.schemas == [ParsedPrompt]
    assert "Android under $300" in model.messages[-1].content
    assert capture.run("rag.parse")["tags"] == ["rag"]


async def test_parse_prompt_repeats_an_invalid_output_once(monkeypatch: pytest.MonkeyPatch) -> None:
    invalid = SearchGuardrailVerdict(allowed=True)
    model = StubChatModel(invalid, SEARCH)
    monkeypatch.setattr(rag_ai, "get_search_model", lambda: model)
    assert await rag_service.parse_prompt("Android under $300") == SEARCH
    assert model.calls == 2


async def test_parse_prompt_raises_after_two_invalid_outputs(monkeypatch: pytest.MonkeyPatch) -> None:
    invalid = SearchGuardrailVerdict(allowed=True)
    model = StubChatModel(invalid, invalid)
    monkeypatch.setattr(rag_ai, "get_search_model", lambda: model)
    with pytest.raises(ValidationError):
        await rag_service.parse_prompt("Android under $300")
    assert model.calls == 2
