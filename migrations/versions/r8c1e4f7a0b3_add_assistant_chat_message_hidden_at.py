"""add assistant_chat_messages.hidden_at

Revision ID: r8c1e4f7a0b3
Revises: q7b0d3e6f9a2
Create Date: 2026-09-26 14:15:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "r8c1e4f7a0b3"
down_revision: Union[str, Sequence[str], None] = "q7b0d3e6f9a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "assistant_chat_messages",
        sa.Column("hidden_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("assistant_chat_messages", "hidden_at")
