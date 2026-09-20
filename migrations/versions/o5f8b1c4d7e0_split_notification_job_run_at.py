"""split notification_jobs.run_at into scheduled_at and next_run_at

Revision ID: o5f8b1c4d7e0
Revises: n4e7a0b3c6d9
Create Date: 2026-09-20 23:25:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "o5f8b1c4d7e0"
down_revision: Union[str, Sequence[str], None] = "n4e7a0b3c6d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "notification_jobs",
        "run_at",
        new_column_name="scheduled_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.add_column(
        "notification_jobs",
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        sa.text("UPDATE notification_jobs SET next_run_at = scheduled_at")
    )
    op.alter_column(
        "notification_jobs",
        "next_run_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )
    op.drop_index(
        "ix_notification_jobs_status_run_at",
        table_name="notification_jobs",
    )
    op.create_index(
        "ix_notification_jobs_status_next_run_at",
        "notification_jobs",
        ["status", "next_run_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_notification_jobs_status_next_run_at",
        table_name="notification_jobs",
    )
    op.create_index(
        "ix_notification_jobs_status_run_at",
        "notification_jobs",
        ["status", "scheduled_at"],
        unique=False,
    )
    op.drop_column("notification_jobs", "next_run_at")
    op.alter_column(
        "notification_jobs",
        "scheduled_at",
        new_column_name="run_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
