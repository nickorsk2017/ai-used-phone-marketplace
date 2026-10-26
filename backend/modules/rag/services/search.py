"""Search entry point of `modules/rag`: docs/ai/RAG.md#module-interface."""

from sqlalchemy.ext.asyncio import AsyncSession

from modules.rag.schemas.search import SearchResult
from modules.rag.services import graph


async def search(session: AsyncSession, prompt: str) -> SearchResult:
    """Ranked listing IDs, at most 20, or the clarification text for a prompt without phone criteria.
    Raises `PromptBlocked` when Guardrail 2 blocks the prompt."""
    return await graph.run(session, prompt)
