"""seed box designs

Revision ID: a1c4f7d2e9b3
Revises: df9ac056b9bf
Create Date: 2026-07-29 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "a1c4f7d2e9b3"
down_revision: Union[str, Sequence[str], None] = "df9ac056b9bf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


box_designs = sa.table(
    "box_designs",
    sa.column("id", sa.Uuid),
    sa.column("code", sa.String),
    sa.column("name", sa.String),
    sa.column("description", sa.Text),
    sa.column("preview_image_url", sa.Text),
    sa.column("theme_config", postgresql.JSONB),
    sa.column("is_active", sa.Boolean),
    sa.column("sort_order", sa.Integer),
)

DESIGNS: list[dict] = [
    {
        "id": "6f1a1d5e-0000-4000-8000-000000000001",
        "code": "romantic",
        "name": "Любовная ночь",
        "description": "Ночное небо и парящие сердца.",
        "theme_config": {
            "gradient": ["#1e1b4b", "#4c1d95", "#831843"],
            "accent": "#f472b6",
            "text": "#fdf2f8",
            "particle": "heart",
            "cover_object_position": "50% 35%",
            "background_image_url": None,
            "gift_box": {
                "body": "#f0a8c8",
                "bodyDark": "#b4487a",
                "lid": "#f4b8d4",
                "lidLight": "#ffd9ea",
                "ribbon": "#ffd775",
                "ribbonDark": "#b8820f",
            },
        },
        "sort_order": 1,
    },
    {
        "id": "6f1a1d5e-0000-4000-8000-000000000002",
        "code": "birthday",
        "name": "День рождения",
        "description": "Конфетти и яркое поздравление.",
        "theme_config": {
            "gradient": ["#2e1065", "#7c3aed", "#f59e0b"],
            "accent": "#fbbf24",
            "text": "#fffbeb",
            "particle": "confetti",
            "cover_object_position": "50% 40%",
            "background_image_url": None,
            "gift_box": {
                "body": "#c9b6fe",
                "bodyDark": "#6d28d9",
                "lid": "#ddd0ff",
                "lidLight": "#efe8ff",
                "ribbon": "#fcc44d",
                "ribbonDark": "#b8650a",
            },
        },
        "sort_order": 2,
    },
    {
        "id": "6f1a1d5e-0000-4000-8000-000000000003",
        "code": "winter",
        "name": "Зимняя сказка",
        "description": "Мороз, снежинки и сияние.",
        "theme_config": {
            "gradient": ["#0b1120", "#0e7490", "#a5f3fc"],
            "accent": "#67e8f9",
            "text": "#ecfeff",
            "particle": "snow",
            "cover_object_position": "50% 40%",
            "background_image_url": None,
            "gift_box": {
                "body": "#9fe9f7",
                "bodyDark": "#0e7490",
                "lid": "#c4f2fb",
                "lidLight": "#e8fdff",
                "ribbon": "#ffe08a",
                "ribbonDark": "#a97706",
            },
        },
        "sort_order": 3,
    },
    {
        "id": "6f1a1d5e-0000-4000-8000-000000000004",
        "code": "golden",
        "name": "Годовщина",
        "description": "Чёрный бархат и золото.",
        "theme_config": {
            "gradient": ["#0c0a09", "#292524", "#a16207"],
            "accent": "#fcd34d",
            "text": "#fef3c7",
            "particle": "sparkle",
            "cover_object_position": "65% 40%",
            "background_image_url": None,
            "gift_box": {
                "body": "#e5e2df",
                "bodyDark": "#8a807a",
                "lid": "#efedeb",
                "lidLight": "#fdfcfb",
                "ribbon": "#fcd34d",
                "ribbonDark": "#96600a",
            },
        },
        "sort_order": 4,
    },
    {
        "id": "6f1a1d5e-0000-4000-8000-000000000005",
        "code": "spring",
        "name": "Весенний сад",
        "description": "Свежесть и лёгкие лепестки.",
        "theme_config": {
            "gradient": ["#052e16", "#15803d", "#f9a8d4"],
            "accent": "#86efac",
            "text": "#f0fdf4",
            "particle": "petal",
            "cover_object_position": "50% 45%",
            "background_image_url": None,
            "gift_box": {
                "body": "#feadb8",
                "bodyDark": "#d6244c",
                "lid": "#ffc6ce",
                "lidLight": "#ffe6ea",
                "ribbon": "#7fe8a4",
                "ribbonDark": "#0f7a41",
            },
        },
        "sort_order": 5,
    },
    {
        "id": "6f1a1d5e-0000-4000-8000-000000000006",
        "code": "retro",
        "name": "Пиксель ретро",
        "description": "Неон и пиксели восьмидесятых.",
        "theme_config": {
            "gradient": ["#020617", "#1e1b4b", "#0891b2"],
            "accent": "#22d3ee",
            "text": "#e0f2fe",
            "particle": "pixel",
            "cover_object_position": "50% 55%",
            "background_image_url": None,
            "gift_box": {
                "body": "#6fe4f5",
                "bodyDark": "#0b6d86",
                "lid": "#a2f0fb",
                "lidLight": "#e2fdff",
                "ribbon": "#b9a5fc",
                "ribbonDark": "#5b21b6",
            },
        },
        "sort_order": 6,
    },
]


def upgrade() -> None:
    op.bulk_insert(
        box_designs,
        [
            {
                **design,
                "preview_image_url": f"https://cdn.pixelgift.app/designs/{design['code']}.jpg",
                "is_active": True,
            }
            for design in DESIGNS
        ],
    )


def downgrade() -> None:
    codes = [design["code"] for design in DESIGNS]
    op.execute(
        box_designs.delete().where(box_designs.c.code.in_(codes))
    )
