"""nullable media_file_id for text box items

Revision ID: c3f6b9d4a1e2
Revises: b2e5a8c3f0d4
Create Date: 2026-07-29 15:40:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3f6b9d4a1e2"
down_revision: Union[str, Sequence[str], None] = "b2e5a8c3f0d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "box_items",
        "media_file_id",
        existing_type=sa.Uuid(),
        nullable=True,
    )


def downgrade() -> None:
    op.execute("DELETE FROM box_items WHERE media_file_id IS NULL")
    op.alter_column(
        "box_items",
        "media_file_id",
        existing_type=sa.Uuid(),
        nullable=False,
    )
