"""Search pipeline as a LangGraph graph, one node per step: docs/ai/RAG.md#architecture.

The request session is passed in the run config (`configurable.session`), not in the state.
"""

import json
import logging
import uuid
from functools import lru_cache
from typing import TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import RetryPolicy
from langsmith import get_current_run_tree
from sqlalchemy.ext.asyncio import AsyncSession

from core.llm import INVALID_LLM_OUTPUT, LLM_VALIDATION_ATTEMPTS
from modules.rag.config import get_settings
from modules.rag.prompts.delimiters import prompt_message
from modules.rag.prompts.guardrail import GUARDRAIL_SYSTEM
from modules.rag.prompts.parse import PARSE_SYSTEM
from modules.rag.prompts.rerank import RERANK_SYSTEM, rerank_message
from modules.rag.schemas.search import (
    Candidate,
    ParsedPrompt,
    PromptBlocked,
    RerankOutput,
    SearchGuardrailVerdict,
    SearchResult,
)
from modules.rag.services import ai, crud, ranking

logger = logging.getLogger(__name__)

SEARCH_RUN_NAME = "rag.search"

# Validation errors only, no wait: network errors are retried by the client.
VALIDATION_RETRY = RetryPolicy(
    max_attempts=LLM_VALIDATION_ATTEMPTS,
    initial_interval=0,
    jitter=False,
    retry_on=lambda error: isinstance(error, INVALID_LLM_OUTPUT),
)


class SearchState(TypedDict, total=False):
    prompt: str
    parsed: ParsedPrompt
    by_code: list[Candidate]
    by_vector: list[Candidate]
    candidates: list[Candidate]
    result: list[uuid.UUID]


def _session(config: RunnableConfig) -> AsyncSession:
    return config["configurable"]["session"]


async def guardrail(state: SearchState) -> SearchState:
    """Guardrail 2, fail closed: docs/ai/GUARDRAILS.md#guardrail-2-search-prompt."""
    verdict = await ai.structured_call(
        ai.get_guardrail_model(),
        SearchGuardrailVerdict,
        GUARDRAIL_SYSTEM,
        prompt_message(state["prompt"]),
    )
    if not verdict.allowed:
        raise PromptBlocked
    return {}


async def parse(state: SearchState) -> SearchState:
    parsed = await ai.structured_call(
        ai.get_search_model(), ParsedPrompt, PARSE_SYSTEM, prompt_message(state["prompt"])
    )
    return {"parsed": parsed}


def needs_clarification(state: SearchState) -> str:
    """A prompt without phone criteria ends the pipeline: docs/ai/RAG.md#clarification."""
    return END if state["parsed"].clarification is not None else "retrieve_by_code"


async def retrieve_by_code(state: SearchState, config: RunnableConfig) -> SearchState:
    parsed = state["parsed"]
    return {"by_code": await crud.find_by_model_codes(_session(config), parsed.model_ids, parsed.filters)}


def needs_vector(state: SearchState) -> str:
    return "retrieve_by_vector" if len(state["by_code"]) < ranking.RESULTS_LIMIT else "merge"


async def retrieve_by_vector(state: SearchState, config: RunnableConfig) -> SearchState:
    parsed = state["parsed"]
    embedding = await ai.embed_query(parsed.query_for_embedding)
    exclude = [candidate.phone_id for candidate in state["by_code"]]
    return {"by_vector": await crud.find_by_vector(_session(config), embedding, parsed.filters, exclude)}


async def merge(state: SearchState) -> SearchState:
    return {"candidates": ranking.merge(state.get("by_code", []), state.get("by_vector", []))}


def _listing(candidate: Candidate) -> dict:
    return candidate.model_dump(mode="json", exclude={"source", "distance"})


def _mark_rerank_fallback(error: Exception) -> None:
    """Metadata of the `rerank` span: docs/ai/EVALUATION.md#tracing. No span when tracing is off."""
    run = get_current_run_tree()
    if run is not None:
        run.add_metadata({"rerank_fallback": True, "rerank_error": type(error).__name__})


async def rerank(state: SearchState) -> SearchState:
    """One LLM call; on any error the candidates are returned without it: docs/ai/RERANKING.md#errors."""
    candidates = state["candidates"]
    parsed = state["parsed"]
    prefer_condition = parsed.filters.condition is None
    single_model = len(parsed.model_ids) == 1
    if not candidates:
        return {"result": []}
    try:
        request = json.dumps(
            {"query": parsed.query_for_embedding, "preferences": parsed.preferences.model_dump(exclude_none=True)}
        )
        listings = "\n".join(json.dumps(_listing(candidate)) for candidate in candidates)
        output = await ai.structured_call(
            ai.get_rerank_model(), RerankOutput, RERANK_SYSTEM, rerank_message(request, listings)
        )
        scores = ranking.validate_scores(output, candidates)
        ranked = ranking.rank(candidates, scores, get_settings().rerank_threshold, prefer_condition)
    except Exception as error:
        logger.exception("Reranking failed, the candidates are returned without reranking")
        _mark_rerank_fallback(error)
        ranked = ranking.fallback_order(candidates, prefer_condition)
    return {"result": ranking.top(ranking.diversity_limit(ranked, single_model))}


@lru_cache
def get_graph() -> CompiledStateGraph:
    graph = StateGraph(SearchState)
    graph.add_node("guardrail", guardrail, retry_policy=VALIDATION_RETRY)
    graph.add_node("parse", parse, retry_policy=VALIDATION_RETRY)
    graph.add_node("retrieve_by_code", retrieve_by_code)
    graph.add_node("retrieve_by_vector", retrieve_by_vector)
    graph.add_node("merge", merge)
    graph.add_node("rerank", rerank)
    graph.add_edge(START, "guardrail")
    graph.add_edge("guardrail", "parse")
    graph.add_conditional_edges("parse", needs_clarification, [END, "retrieve_by_code"])
    graph.add_conditional_edges("retrieve_by_code", needs_vector, ["retrieve_by_vector", "merge"])
    graph.add_edge("retrieve_by_vector", "merge")
    graph.add_edge("merge", "rerank")
    graph.add_edge("rerank", END)
    return graph.compile()


async def run(session: AsyncSession, prompt: str) -> SearchResult:
    # Root run `rag.search`, one child span per node: docs/ai/EVALUATION.md#tracing. The session is not a
    # primitive value, so LangChain does not copy it from `configurable` to the trace metadata.
    config: RunnableConfig = {"run_name": SEARCH_RUN_NAME, "tags": ["rag"], "configurable": {"session": session}}
    state = await get_graph().ainvoke({"prompt": prompt}, config=config)
    clarification = state["parsed"].clarification
    if clarification is not None:
        return SearchResult(clarification=clarification)
    return SearchResult(phone_ids=state["result"])
