"""Database functions of `modules/rag`.

They use the session of the request and never commit: docs/backend/DESIGN.md#database-connection.
"""

import uuid
from collections.abc import Sequence

from sqlalchemy import ColumnElement, Select, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.rag.models import SearchIndex
from modules.rag.schemas import IndexedPhone
from modules.rag.schemas.search import Candidate, Filters

CODE_CANDIDATES_LIMIT = 40
VECTOR_CANDIDATES_LIMIT = 20

_OPERATORS = {
    "<=": lambda column, value: column <= value,
    ">=": lambda column, value: column >= value,
    "<": lambda column, value: column < value,
    ">": lambda column, value: column > value,
    "=": lambda column, value: column == value,
}


async def index(session: AsyncSession, phone: IndexedPhone, embedding: list[float]) -> None:
    """Creates the search index record of a new listing, in the transaction of the listing."""
    await session.execute(insert(SearchIndex).values(**phone.model_dump(), embedding=embedding))


def filter_conditions(filters: Filters) -> list[ColumnElement[bool]]:
    """`WHERE` of condition and price set in the prompt only: docs/ai/RAG.md#search-index-table."""
    conditions: list[ColumnElement[bool]] = []
    if filters.condition is not None:
        conditions.append(SearchIndex.condition.in_(filters.condition.value))
    if filters.price is not None:
        conditions.append(_OPERATORS[filters.price.operator](SearchIndex.price, filters.price.value))
        if filters.price.max_value is not None:
            conditions.append(SearchIndex.price <= filters.price.max_value)
    return conditions


def _candidates_query(filters: Filters) -> Select[tuple[SearchIndex]]:
    return select(SearchIndex).where(*filter_conditions(filters))


async def find_by_model_codes(
    session: AsyncSession, codes: Sequence[str], filters: Filters, limit: int = CODE_CANDIDATES_LIMIT
) -> list[Candidate]:
    """Listings of the model codes from the LLM, exact match: docs/ai/RAG.md#model-code."""
    if not codes:
        return []
    statement = (
        _candidates_query(filters)
        .where(SearchIndex.model_code.in_(list(codes)))
        .order_by(SearchIndex.updated_at.desc(), SearchIndex.phone_id)
        .limit(limit)
    )
    rows = await session.scalars(statement)
    return [Candidate.model_validate(row) for row in rows]


async def find_by_vector(
    session: AsyncSession,
    embedding: list[float],
    filters: Filters,
    exclude_ids: Sequence[uuid.UUID] = (),
    limit: int = VECTOR_CANDIDATES_LIMIT,
) -> list[Candidate]:
    """pgvector search with condition and price in the same query: docs/ai/RAG.md#search-index-table."""
    distance = SearchIndex.embedding.cosine_distance(embedding).label("distance")
    statement = select(SearchIndex, distance).where(*filter_conditions(filters)).order_by(distance).limit(limit)
    if exclude_ids:
        statement = statement.where(SearchIndex.phone_id.not_in(list(exclude_ids)))
    rows = await session.execute(statement)
    return [
        Candidate.model_validate(row).model_copy(update={"source": "vector", "distance": float(value)})
        for row, value in rows
    ]
