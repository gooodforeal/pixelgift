"""extend design theme_config and add design_assets

Revision ID: e5b8d1f6c3a2
Revises: d4a7c0e5b2f1
Create Date: 2026-08-03 22:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e5b8d1f6c3a2"
down_revision: Union[str, Sequence[str], None] = "d4a7c0e5b2f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


THEME_EXTRAS: dict[str, dict] = {
    "romantic": {
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
    "birthday": {
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
    "winter": {
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
    "golden": {
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
    "spring": {
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
    "retro": {
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
}


def upgrade() -> None:
    op.create_table(
        "design_assets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("storage_key", sa.Text(), nullable=False),
        sa.Column("mime_type", sa.String(length=128), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("original_filename", sa.String(length=512), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    connection = op.get_bind()
    rows = connection.execute(
        sa.text("SELECT id, code, theme_config FROM box_designs")
    ).mappings()
    for row in rows:
        extras = THEME_EXTRAS.get(row["code"])
        if extras is None:
            continue
        config = dict(row["theme_config"] or {})
        config.update(extras)
        connection.execute(
            sa.text(
                "UPDATE box_designs SET theme_config = CAST(:config AS jsonb) "
                "WHERE id = :id"
            ),
            {"config": _json_dumps(config), "id": str(row["id"])},
        )


def downgrade() -> None:
    connection = op.get_bind()
    rows = connection.execute(
        sa.text("SELECT id, code, theme_config FROM box_designs")
    ).mappings()
    drop_keys = ("cover_object_position", "background_image_url", "gift_box")
    for row in rows:
        if row["code"] not in THEME_EXTRAS:
            continue
        config = dict(row["theme_config"] or {})
        for key in drop_keys:
            config.pop(key, None)
        connection.execute(
            sa.text(
                "UPDATE box_designs SET theme_config = CAST(:config AS jsonb) "
                "WHERE id = :id"
            ),
            {"config": _json_dumps(config), "id": str(row["id"])},
        )

    op.drop_table("design_assets")


def _json_dumps(value: dict) -> str:
    import json

    return json.dumps(value)
