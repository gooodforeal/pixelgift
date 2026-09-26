"""product sales

Revision ID: y5d8e1f4g7b0
Revises: x4c7d0e3f6a9
Create Date: 2026-09-27 00:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "y5d8e1f4g7b0"
down_revision: Union[str, Sequence[str], None] = "x4c7d0e3f6a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "product_sales",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("discount_percent", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
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
        sa.CheckConstraint(
            "discount_percent >= 5 AND discount_percent <= 100 "
            "AND discount_percent % 5 = 0",
            name="ck_product_sales_discount_percent",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id"),
    )
    op.create_index(
        "ix_product_sales_product_id", "product_sales", ["product_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_product_sales_product_id", table_name="product_sales")
    op.drop_table("product_sales")
