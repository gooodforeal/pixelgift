"""shorten box title, recipient, preview title limits

Revision ID: d4a7c0e5b2f1
Revises: c3f6b9d4a1e2
Create Date: 2026-07-30 22:55:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4a7c0e5b2f1"
down_revision: Union[str, Sequence[str], None] = "c3f6b9d4a1e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE boxes SET title = left(title, 30)")
    op.execute("UPDATE boxes SET recipient_name = left(recipient_name, 30)")
    op.execute(
        "UPDATE boxes SET preview_title = left(preview_title, 30) "
        "WHERE preview_title IS NOT NULL"
    )
    op.execute(
        "UPDATE box_items SET caption = left(caption, 300) "
        "WHERE caption IS NOT NULL AND char_length(caption) > 300"
    )

    op.alter_column(
        "boxes",
        "title",
        existing_type=sa.String(length=256),
        type_=sa.String(length=30),
        existing_nullable=False,
    )
    op.alter_column(
        "boxes",
        "recipient_name",
        existing_type=sa.String(length=128),
        type_=sa.String(length=30),
        existing_nullable=False,
    )
    op.alter_column(
        "boxes",
        "preview_title",
        existing_type=sa.String(length=256),
        type_=sa.String(length=30),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "boxes",
        "preview_title",
        existing_type=sa.String(length=30),
        type_=sa.String(length=256),
        existing_nullable=True,
    )
    op.alter_column(
        "boxes",
        "recipient_name",
        existing_type=sa.String(length=30),
        type_=sa.String(length=128),
        existing_nullable=False,
    )
    op.alter_column(
        "boxes",
        "title",
        existing_type=sa.String(length=30),
        type_=sa.String(length=256),
        existing_nullable=False,
    )
