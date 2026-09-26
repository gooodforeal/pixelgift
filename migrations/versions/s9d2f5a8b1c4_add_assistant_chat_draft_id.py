"""add assistant_chat_messages.draft_id

Revision ID: s9d2f5a8b1c4
Revises: r8c1e4f7a0b3
Create Date: 2026-09-26 15:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "s9d2f5a8b1c4"
down_revision: Union[str, Sequence[str], None] = "r8c1e4f7a0b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "assistant_chat_messages",
        sa.Column("draft_id", sa.Uuid(), nullable=True),
    )
    op.create_index(
        "ix_assistant_chat_messages_user_draft_created",
        "assistant_chat_messages",
        ["user_id", "draft_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_assistant_chat_messages_user_draft_created",
        table_name="assistant_chat_messages",
    )
    op.drop_column("assistant_chat_messages", "draft_id")
