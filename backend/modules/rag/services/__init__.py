"""Public interface of `modules/rag`. Called by `modules/main`: docs/ai/RAG.md#module-interface."""

from modules.rag.services.ai import embed_listing, embedding_input
from modules.rag.services.crud import index
from modules.rag.services.search import search

__all__ = ["embed_listing", "embedding_input", "index", "search"]
