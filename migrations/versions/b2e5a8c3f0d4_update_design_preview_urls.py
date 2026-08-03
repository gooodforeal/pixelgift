"""update design preview image urls

Revision ID: b2e5a8c3f0d4
Revises: a1c4f7d2e9b3
Create Date: 2026-07-29 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "b2e5a8c3f0d4"
down_revision: Union[str, Sequence[str], None] = "a1c4f7d2e9b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CODES = (
    "romantic",
    "birthday",
    "winter",
    "golden",
    "spring",
    "retro",
)


def upgrade() -> None:
    # Stored as absolute URLs for the domain Url value object.
    # The frontend serves the real files from /designs/{code}.jpg.
    for code in CODES:
        op.execute(
            "UPDATE box_designs "
            f"SET preview_image_url = 'https://cdn.pixelgift.app/designs/{code}.jpg' "
            f"WHERE code = '{code}'"
        )


def downgrade() -> None:
    for code in CODES:
        op.execute(
            "UPDATE box_designs "
            f"SET preview_image_url = 'https://pixelgift.app/designs/{code}.png' "
            f"WHERE code = '{code}'"
        )
