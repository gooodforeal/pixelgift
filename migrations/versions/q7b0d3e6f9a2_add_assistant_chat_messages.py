"""add assistant chat messages

Revision ID: q7b0d3e6f9a2
Revises: p6a9c2d5e8f1
Create Date: 2026-09-26 13:35:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "q7b0d3e6f9a2"
down_revision: Union[str, Sequence[str], None] = "p6a9c2d5e8f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "assistant_chat_messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("box_id", sa.Uuid(), nullable=True),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("step", sa.String(length=32), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["box_id"], ["boxes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_assistant_chat_messages_user_box_created",
        "assistant_chat_messages",
        ["user_id", "box_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_assistant_chat_messages_user_box_created",
        table_name="assistant_chat_messages",
    )
    op.drop_table("assistant_chat_messages")
