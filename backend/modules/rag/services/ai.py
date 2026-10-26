"""LLM and embedding calls of `modules/rag`. The clients are created from the settings of the module."""

from functools import lru_cache

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langsmith import traceable
from pydantic import BaseModel

from core.llm import chat_model, embeddings, llm_call
from modules.rag.config import get_settings
from modules.rag.prompts.delimiters import prompt_message
from modules.rag.prompts.parse import PARSE_SYSTEM
from modules.rag.schemas.search import ParsedPrompt


@lru_cache
def get_embeddings() -> Embeddings:
    settings = get_settings()
    return embeddings(settings.openai_api_key, settings.embedding_model)


@lru_cache
def get_guardrail_model() -> BaseChatModel:
    settings = get_settings()
    return chat_model(settings.openai_api_key, settings.guardrail_model)


@lru_cache
def get_search_model() -> BaseChatModel:
    settings = get_settings()
    return chat_model(settings.openai_api_key, settings.search_model)


@lru_cache
def get_rerank_model() -> BaseChatModel:
    settings = get_settings()
    return chat_model(settings.openai_api_key, settings.rerank_model)


def embedding_input(model_name: str, description: str, condition_note: str) -> str:
    """Text of the listing embedding: docs/ai/RAG.md#indexing."""
    return "\n".join(part for part in (model_name, description, condition_note) if part)


# Root run in LangSmith: docs/ai/EVALUATION.md#tracing.
@traceable(name="rag.embed_listing", tags=["rag"])
async def embed_listing(model_name: str, description: str, condition_note: str) -> list[float]:
    """Slow network call: runs before the database work of the request."""
    return await get_embeddings().aembed_query(embedding_input(model_name, description, condition_note))


async def embed_query(text: str) -> list[float]:
    return await get_embeddings().aembed_query(text)


async def structured_call[Output: BaseModel](
    model: BaseChatModel, schema: type[Output], system: str, user: str
) -> Output:
    """One structured LLM call. An invalid output is repeated by the `RetryPolicy` of the graph node,
    not here: docs/ai/RAG.md#errors-and-retries."""
    output = await model.with_structured_output(schema).ainvoke([SystemMessage(system), HumanMessage(user)])
    return schema.model_validate(output, from_attributes=True)


def _to_parsed(output: BaseModel) -> ParsedPrompt:
    return ParsedPrompt.model_validate(output, from_attributes=True)


@traceable(name="rag.parse", tags=["rag"])
async def parse_prompt(prompt: str) -> ParsedPrompt:
    """The LLM call of the search pipeline alone, for the evaluation: docs/ai/RAG.md#module-interface.

    Same model, prompt and one repeat on an invalid output as the `parse` node of the graph, without
    Guardrail 2 and without the database.
    """
    return await llm_call(get_search_model(), ParsedPrompt, PARSE_SYSTEM, prompt_message(prompt), _to_parsed)
