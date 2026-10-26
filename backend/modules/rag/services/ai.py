"""Embedding calls of `modules/rag`. The embeddings client is created from the settings of the module."""

from functools import lru_cache

from langchain_core.embeddings import Embeddings

from core.llm import embeddings
from modules.rag.config import get_settings


@lru_cache
def get_embeddings() -> Embeddings:
    settings = get_settings()
    return embeddings(settings.openai_api_key, settings.embedding_model)


def embedding_input(model_name: str, description: str, condition_note: str) -> str:
    """Text of the listing embedding: docs/ai/RAG.md#indexing."""
    return "\n".join(part for part in (model_name, description, condition_note) if part)


async def embed_listing(model_name: str, description: str, condition_note: str) -> list[float]:
    """Slow network call: runs before the database work of the request."""
    return await get_embeddings().aembed_query(embedding_input(model_name, description, condition_note))
