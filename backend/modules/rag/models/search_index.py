import uuid
from datetime import datetime
from decimal import Decimal

from pgvector.sqlalchemy import Vector
from sqlalchemy import UUID, DateTime, Enum, Index, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from modules.rag.database import RagBase

# Same length as `phones.model_code`: docs/backend/SCHEMAS.md#phones-modulesphones.
MODEL_CODE_MAX_LENGTH = 32

# OpenAI `text-embedding-3-small`: docs/backend/SCHEMAS.md#search_index-modulesrag.
EMBEDDING_DIMENSIONS = 1536


class SearchIndex(RagBase):
    """`search_index` table, the read model of the search: docs/backend/SCHEMAS.md#search_index-modulesrag.

    The enum types are owned by `modules/phones` (migration `0002`), the copies reuse them by name.
    """

    __tablename__ = "search_index"
    __table_args__ = (
        Index(
            "ix_search_index_embedding",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    phone_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIMENSIONS))
    model_code: Mapped[str] = mapped_column(String(MODEL_CODE_MAX_LENGTH))
    model_name: Mapped[str] = mapped_column(String(200))
    os: Mapped[str] = mapped_column(Enum("ios", "android", name="phone_os", create_type=False))
    camera_megapixels: Mapped[int] = mapped_column(Integer)
    battery_capacity: Mapped[int] = mapped_column(Integer)
    display_size: Mapped[Decimal] = mapped_column(Numeric(4, 2))
    description: Mapped[str] = mapped_column(Text)
    condition_note: Mapped[str] = mapped_column(Text)
    condition: Mapped[str] = mapped_column(
        Enum("like_new", "average", "for_repair", name="phone_condition", create_type=False)
    )
    price: Mapped[int] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
