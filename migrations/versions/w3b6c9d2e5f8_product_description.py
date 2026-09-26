"""product description

Revision ID: w3b6c9d2e5f8
Revises: v2a5b8c1d4e7
Create Date: 2026-09-26 21:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "w3b6c9d2e5f8"
down_revision: Union[str, Sequence[str], None] = "v2a5b8c1d4e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BOX_CREDIT_DESCRIPTION = (
    "Кредит на создание одного виртуального бокса-подарка. "
    "После оплаты кредит появится на балансе и спишется при создании бокса."
)


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
    )
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE products SET description = :description WHERE sku = 'box_credit'"
        ),
        {"description": BOX_CREDIT_DESCRIPTION},
    )


def downgrade() -> None:
    op.drop_column("products", "description")
