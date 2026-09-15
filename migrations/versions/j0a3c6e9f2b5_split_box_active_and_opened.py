"""split box active and opened statuses

Revision ID: j0a3c6e9f2b5
Revises: i9f2b5d8e1a4
Create Date: 2026-09-15 21:05:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "j0a3c6e9f2b5"
down_revision: Union[str, Sequence[str], None] = "i9f2b5d8e1a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE boxes
            SET status = 'opened'
            WHERE first_opened_at IS NOT NULL
              AND status IN ('active', 'scheduled')
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE boxes
            SET status = 'active'
            WHERE first_opened_at IS NULL
              AND status = 'scheduled'
              AND activates_at <= NOW()
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE boxes
            SET status = 'active'
            WHERE status = 'opened'
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE boxes
            SET status = 'scheduled'
            WHERE status = 'active'
              AND first_opened_at IS NULL
            """
        )
    )
