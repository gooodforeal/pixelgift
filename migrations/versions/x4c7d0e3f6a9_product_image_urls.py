"""product image urls

Revision ID: x4c7d0e3f6a9
Revises: w3b6c9d2e5f8
Create Date: 2026-09-26 21:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "x4c7d0e3f6a9"
down_revision: Union[str, Sequence[str], None] = "w3b6c9d2e5f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column(
            "image_urls",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column("products", "image_urls")
