"""promo max usages

Revision ID: z6e9f2g5h8c1
Revises: y5d8e1f4g7b0
Create Date: 2026-09-27 18:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "z6e9f2g5h8c1"
down_revision: Union[str, Sequence[str], None] = "y5d8e1f4g7b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "promo_codes",
        sa.Column("max_usages", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("promo_codes", "max_usages")
