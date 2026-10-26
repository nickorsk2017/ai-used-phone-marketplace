"""`modules/rag` indexing: docs/ai/RAG.md#indexing."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from conftest import EMBEDDING_DIMENSIONS, AiStubs
from modules.rag import services as rag_service
from modules.rag.models import SearchIndex
from modules.rag.schemas import IndexedPhone


def test_embedding_input_joins_the_texts() -> None:
    assert rag_service.embedding_input("iPhone 13 Pro", "Description", "") == "iPhone 13 Pro\nDescription"


async def test_embed_listing_uses_the_listing_text(ai_stubs: AiStubs) -> None:
    embeddings = ai_stubs.embeddings
    vector = await rag_service.embed_listing("Pixel 8", "Google phone", "Like new")
    assert len(vector) == EMBEDDING_DIMENSIONS
    assert embeddings.texts == ["Pixel 8\nGoogle phone\nLike new"]


async def test_index_stores_the_copied_fields(session: AsyncSession) -> None:
    phone = IndexedPhone(
        phone_id=uuid.uuid4(),
        model_code="GKWS6",
        model_name="Pixel 8",
        os="android",
        camera_megapixels=50,
        battery_capacity=4575,
        display_size=Decimal("6.2"),
        description="Google phone",
        condition_note="Like new",
        condition="like_new",
        price=380,
        updated_at=datetime.now(UTC),
    )
    await rag_service.index(session, phone, [0.5] * EMBEDDING_DIMENSIONS)
    row = await session.scalar(select(SearchIndex).where(SearchIndex.phone_id == phone.phone_id))
    assert row is not None
    assert row.price == 380
    assert row.condition == "like_new"
    assert len(row.embedding) == EMBEDDING_DIMENSIONS
