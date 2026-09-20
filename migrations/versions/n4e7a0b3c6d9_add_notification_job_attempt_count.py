"""add notification_jobs.attempt_count

Revision ID: n4e7a0b3c6d9
Revises: m3d6f9a2c5e8
Create Date: 2026-09-20 23:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "n4e7a0b3c6d9"
down_revision: Union[str, Sequence[str], None] = "m3d6f9a2c5e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "notification_jobs",
        sa.Column(
            "attempt_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("notification_jobs", "attempt_count")
