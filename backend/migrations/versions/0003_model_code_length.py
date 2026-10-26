"""Limit model_code to 32 characters

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLES = ("phones", "search_index")


def upgrade() -> None:
    # The schema already limits model_code to 32 characters: docs/backend/SCHEMAS.md#phones-modulesphones.
    for table in TABLES:
        op.alter_column(table, "model_code", type_=sa.String(length=32), existing_type=sa.String(length=64))


def downgrade() -> None:
    for table in TABLES:
        op.alter_column(table, "model_code", type_=sa.String(length=64), existing_type=sa.String(length=32))
