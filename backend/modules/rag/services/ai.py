"""LLM and embedding calls of `modules/rag`. The clients are created from the settings of the module."""

from functools import lru_cache

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from core.llm import chat_model, embeddings
from modules.rag.config import get_settings


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
