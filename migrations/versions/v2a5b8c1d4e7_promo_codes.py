"""promo codes

Revision ID: v2a5b8c1d4e7
Revises: u1f4a7b0c3d6
Create Date: 2026-09-26 21:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "v2a5b8c1d4e7"
down_revision: Union[str, Sequence[str], None] = "u1f4a7b0c3d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "promo_codes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("discount_percent", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("usage_count", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["created_by_user_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.add_column(
        "orders",
        sa.Column("promo_code_id", sa.Uuid(), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("discount_percent", sa.Integer(), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("amount_before_discount", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_orders_promo_code_id",
        "orders",
        "promo_codes",
        ["promo_code_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_orders_promo_code_id", "orders", ["promo_code_id"])


def downgrade() -> None:
    op.drop_index("ix_orders_promo_code_id", table_name="orders")
    op.drop_constraint("fk_orders_promo_code_id", "orders", type_="foreignkey")
    op.drop_column("orders", "amount_before_discount")
    op.drop_column("orders", "discount_percent")
    op.drop_column("orders", "promo_code_id")
    op.drop_table("promo_codes")
