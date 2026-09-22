"""add users.notifications_enabled

Revision ID: p6a9c2d5e8f1
Revises: o5f8b1c4d7e0
Create Date: 2026-09-22 17:45:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "p6a9c2d5e8f1"
down_revision: Union[str, Sequence[str], None] = "o5f8b1c4d7e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "notifications_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "notifications_enabled")
