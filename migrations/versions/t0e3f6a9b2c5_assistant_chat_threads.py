"""assistant chat threads

Revision ID: t0e3f6a9b2c5
Revises: s9d2f5a8b1c4
Create Date: 2026-09-26 16:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "t0e3f6a9b2c5"
down_revision: Union[str, Sequence[str], None] = "s9d2f5a8b1c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "assistant_chat_threads",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("box_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["box_id"], ["boxes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("box_id"),
    )
    op.create_index(
        "ix_assistant_chat_threads_user_id",
        "assistant_chat_threads",
        ["user_id"],
    )

    op.add_column(
        "assistant_chat_messages",
        sa.Column("thread_id", sa.Uuid(), nullable=True),
    )

    # One thread per existing box conversation.
    op.execute(
        """
        INSERT INTO assistant_chat_threads (id, user_id, box_id, created_at)
        SELECT gen_random_uuid(), user_id, box_id, MIN(created_at)
        FROM assistant_chat_messages
        WHERE box_id IS NOT NULL
        GROUP BY user_id, box_id
        """
    )
    # Draft conversations keep draft_id as the new thread id.
    op.execute(
        """
        INSERT INTO assistant_chat_threads (id, user_id, box_id, created_at)
        SELECT draft_id, user_id, NULL, MIN(created_at)
        FROM assistant_chat_messages
        WHERE box_id IS NULL AND draft_id IS NOT NULL
        GROUP BY user_id, draft_id
        """
    )

    op.execute(
        """
        UPDATE assistant_chat_messages AS m
        SET thread_id = t.id
        FROM assistant_chat_threads AS t
        WHERE m.box_id IS NOT NULL
          AND t.box_id = m.box_id
          AND t.user_id = m.user_id
        """
    )
    op.execute(
        """
        UPDATE assistant_chat_messages AS m
        SET thread_id = m.draft_id
        WHERE m.box_id IS NULL AND m.draft_id IS NOT NULL
        """
    )
    # Orphan rows (no box, no draft): one thread per user, then attach.
    op.execute(
        """
        WITH orphan_users AS (
            SELECT user_id, MIN(created_at) AS created_at
            FROM assistant_chat_messages
            WHERE box_id IS NULL AND draft_id IS NULL AND thread_id IS NULL
            GROUP BY user_id
        ),
        inserted AS (
            INSERT INTO assistant_chat_threads (id, user_id, box_id, created_at)
            SELECT gen_random_uuid(), user_id, NULL, created_at
            FROM orphan_users
            RETURNING id, user_id
        )
        UPDATE assistant_chat_messages AS m
        SET thread_id = i.id
        FROM inserted AS i
        WHERE m.user_id = i.user_id
          AND m.box_id IS NULL
          AND m.draft_id IS NULL
          AND m.thread_id IS NULL
        """
    )

    op.alter_column(
        "assistant_chat_messages",
        "thread_id",
        existing_type=sa.Uuid(),
        nullable=False,
    )
    op.create_foreign_key(
        "fk_assistant_chat_messages_thread_id",
        "assistant_chat_messages",
        "assistant_chat_threads",
        ["thread_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_assistant_chat_messages_thread_created",
        "assistant_chat_messages",
        ["thread_id", "created_at"],
    )

    op.drop_index(
        "ix_assistant_chat_messages_user_box_created",
        table_name="assistant_chat_messages",
    )
    op.drop_index(
        "ix_assistant_chat_messages_user_draft_created",
        table_name="assistant_chat_messages",
    )
    op.drop_constraint(
        "assistant_chat_messages_box_id_fkey",
        "assistant_chat_messages",
        type_="foreignkey",
    )
    op.drop_constraint(
        "assistant_chat_messages_user_id_fkey",
        "assistant_chat_messages",
        type_="foreignkey",
    )
    op.drop_column("assistant_chat_messages", "draft_id")
    op.drop_column("assistant_chat_messages", "box_id")
    op.drop_column("assistant_chat_messages", "user_id")


def downgrade() -> None:
    op.add_column(
        "assistant_chat_messages",
        sa.Column("user_id", sa.Uuid(), nullable=True),
    )
    op.add_column(
        "assistant_chat_messages",
        sa.Column("box_id", sa.Uuid(), nullable=True),
    )
    op.add_column(
        "assistant_chat_messages",
        sa.Column("draft_id", sa.Uuid(), nullable=True),
    )

    op.execute(
        """
        UPDATE assistant_chat_messages AS m
        SET user_id = t.user_id,
            box_id = t.box_id,
            draft_id = CASE WHEN t.box_id IS NULL THEN t.id ELSE NULL END
        FROM assistant_chat_threads AS t
        WHERE m.thread_id = t.id
        """
    )

    op.alter_column(
        "assistant_chat_messages",
        "user_id",
        existing_type=sa.Uuid(),
        nullable=False,
    )
    op.create_foreign_key(
        "assistant_chat_messages_user_id_fkey",
        "assistant_chat_messages",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "assistant_chat_messages_box_id_fkey",
        "assistant_chat_messages",
        "boxes",
        ["box_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_assistant_chat_messages_user_box_created",
        "assistant_chat_messages",
        ["user_id", "box_id", "created_at"],
    )
    op.create_index(
        "ix_assistant_chat_messages_user_draft_created",
        "assistant_chat_messages",
        ["user_id", "draft_id", "created_at"],
    )

    op.drop_index(
        "ix_assistant_chat_messages_thread_created",
        table_name="assistant_chat_messages",
    )
    op.drop_constraint(
        "fk_assistant_chat_messages_thread_id",
        "assistant_chat_messages",
        type_="foreignkey",
    )
    op.drop_column("assistant_chat_messages", "thread_id")

    op.drop_index(
        "ix_assistant_chat_threads_user_id",
        table_name="assistant_chat_threads",
    )
    op.drop_table("assistant_chat_threads")
