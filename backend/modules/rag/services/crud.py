"""Database functions of `modules/rag`.

They use the session of the request and never commit: docs/backend/DESIGN.md#database-connection.
"""

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from modules.rag.models import SearchIndex
from modules.rag.schemas import IndexedPhone


async def index(session: AsyncSession, phone: IndexedPhone, embedding: list[float]) -> None:
    """Creates the search index record of a new listing, in the transaction of the listing."""
    await session.execute(insert(SearchIndex).values(**phone.model_dump(), embedding=embedding))
