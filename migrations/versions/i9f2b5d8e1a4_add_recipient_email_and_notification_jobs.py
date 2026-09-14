"""add recipient email and notification_jobs

Revision ID: i9f2b5d8e1a4
Revises: h8e1a4c9d6f3
Create Date: 2026-09-14 22:40:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "i9f2b5d8e1a4"
down_revision: Union[str, Sequence[str], None] = "h8e1a4c9d6f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "boxes",
        sa.Column("recipient_email", sa.String(length=254), nullable=True),
    )
    op.create_table(
        "notification_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("box_id", sa.Uuid(), nullable=False),
        sa.Column("template", sa.String(length=32), nullable=False),
        sa.Column("run_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["box_id"], ["boxes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "box_id",
            "template",
            name="uq_notification_jobs_box_id_template",
        ),
    )
    op.create_index(
        "ix_notification_jobs_status_run_at",
        "notification_jobs",
        ["status", "run_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_notification_jobs_status_run_at",
        table_name="notification_jobs",
    )
    op.drop_table("notification_jobs")
    op.drop_column("boxes", "recipient_email")
