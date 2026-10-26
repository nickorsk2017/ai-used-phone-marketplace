"""Create phones and search_index

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-26
"""

from collections.abc import Sequence

import pgvector.sqlalchemy
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PHONE_OS = postgresql.ENUM("ios", "android", name="phone_os", create_type=False)
PHONE_CONDITION = postgresql.ENUM("like_new", "average", "for_repair", name="phone_condition", create_type=False)


def upgrade() -> None:
    # The extension is shared by the database and is kept on downgrade: docs/backend/SCHEMAS.md#migrations.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    PHONE_OS.create(op.get_bind(), checkfirst=True)
    PHONE_CONDITION.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "phones",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("model_code", sa.String(length=64), nullable=False),
        sa.Column("model_name", sa.String(length=200), nullable=False),
        sa.Column("os", PHONE_OS, nullable=False),
        sa.Column("camera_megapixels", sa.Integer(), nullable=False),
        sa.Column("battery_capacity", sa.Integer(), nullable=False),
        sa.Column("display_size", sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("condition", PHONE_CONDITION, nullable=False),
        sa.Column("condition_note", sa.Text(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("price > 0", name="ck_phones_price_positive"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_phones_user_id"), "phones", ["user_id"], unique=False)

    op.create_table(
        "search_index",
        sa.Column("phone_id", sa.UUID(), nullable=False),
        sa.Column("embedding", pgvector.sqlalchemy.Vector(dim=1536), nullable=False),
        sa.Column("model_code", sa.String(length=64), nullable=False),
        sa.Column("model_name", sa.String(length=200), nullable=False),
        sa.Column("os", PHONE_OS, nullable=False),
        sa.Column("camera_megapixels", sa.Integer(), nullable=False),
        sa.Column("battery_capacity", sa.Integer(), nullable=False),
        sa.Column("display_size", sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("condition_note", sa.Text(), nullable=False),
        sa.Column("condition", PHONE_CONDITION, nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("phone_id"),
    )
    op.create_index(
        "ix_search_index_embedding",
        "search_index",
        ["embedding"],
        unique=False,
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_index("ix_search_index_embedding", table_name="search_index", postgresql_using="hnsw")
    op.drop_table("search_index")
    op.drop_index(op.f("ix_phones_user_id"), table_name="phones")
    op.drop_table("phones")
    PHONE_CONDITION.drop(op.get_bind(), checkfirst=True)
    PHONE_OS.drop(op.get_bind(), checkfirst=True)
