"""shorten design name code description limits

Revision ID: f6c9e2a7b4d1
Revises: e5b8d1f6c3a2
Create Date: 2026-08-03 23:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


revision: str = "f6c9e2a7b4d1"
down_revision: Union[str, Sequence[str], None] = "e5b8d1f6c3a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# old_code, new_code, name, description
UPDATES = (
    (
        "romantic-night",
        "romantic",
        "Любовная ночь",
        "Ночное небо и парящие сердца.",
    ),
    (
        "birthday-confetti",
        "birthday",
        "День рождения",
        "Конфетти и яркое поздравление.",
    ),
    (
        "winter-magic",
        "winter",
        "Зимняя сказка",
        "Мороз, снежинки и сияние.",
    ),
    (
        "golden-anniversary",
        "golden",
        "Годовщина",
        "Чёрный бархат и золото.",
    ),
    (
        "spring-bloom",
        "spring",
        "Весенний сад",
        "Свежесть и лёгкие лепестки.",
    ),
    (
        "retro-pixel",
        "retro",
        "Пиксель ретро",
        "Неон и пиксели восьмидесятых.",
    ),
)


def upgrade() -> None:
    for old_code, new_code, name, description in UPDATES:
        op.execute(
            "UPDATE box_designs SET "
            f"code = '{new_code}', "
            f"name = '{name}', "
            f"description = '{description}', "
            f"preview_image_url = 'https://cdn.pixelgift.app/designs/{new_code}.jpg' "
            f"WHERE code = '{old_code}'"
        )


def downgrade() -> None:
    for old_code, new_code, name, description in UPDATES:
        # Restore previous long codes; names/descriptions stay shortened.
        op.execute(
            "UPDATE box_designs SET "
            f"code = '{old_code}', "
            f"preview_image_url = 'https://cdn.pixelgift.app/designs/{old_code}.jpg' "
            f"WHERE code = '{new_code}'"
        )
