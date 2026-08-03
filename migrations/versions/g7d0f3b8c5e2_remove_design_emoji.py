"""remove emoji from design theme_config

Revision ID: g7d0f3b8c5e2
Revises: f6c9e2a7b4d1
Create Date: 2026-08-03 23:15:00.000000

"""

from typing import Sequence, Union
import json

from alembic import op
import sqlalchemy as sa


revision: str = "g7d0f3b8c5e2"
down_revision: Union[str, Sequence[str], None] = "f6c9e2a7b4d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    rows = connection.execute(
        sa.text("SELECT id, theme_config FROM box_designs")
    ).mappings()
    for row in rows:
        config = dict(row["theme_config"] or {})
        if "emoji" not in config:
            continue
        config.pop("emoji", None)
        connection.execute(
            sa.text(
                "UPDATE box_designs SET theme_config = CAST(:config AS jsonb) "
                "WHERE id = :id"
            ),
            {"config": json.dumps(config), "id": str(row["id"])},
        )


def downgrade() -> None:
    # emoji was removed intentionally; no restore
    pass
