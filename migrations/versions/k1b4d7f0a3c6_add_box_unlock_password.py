"""add box unlock password

Revision ID: k1b4d7f0a3c6
Revises: j0a3c6e9f2b5
Create Date: 2026-09-19 22:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "k1b4d7f0a3c6"
down_revision: Union[str, Sequence[str], None] = "j0a3c6e9f2b5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "boxes",
        sa.Column("unlock_password", sa.String(length=12), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("boxes", "unlock_password")
