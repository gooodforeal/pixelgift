"""link box_designs to design_assets

Revision ID: m3d6f9a2c5e8
Revises: l2c5e8a1b4d7
Create Date: 2026-09-19 23:58:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "m3d6f9a2c5e8"
down_revision: Union[str, Sequence[str], None] = "l2c5e8a1b4d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_UUID_RE = (
    r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"
)


def upgrade() -> None:
    op.add_column(
        "box_designs",
        sa.Column("preview_asset_id", sa.Uuid(), nullable=True),
    )
    op.add_column(
        "box_designs",
        sa.Column("preview_asset_id_light", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        "fk_box_designs_preview_asset_id",
        "box_designs",
        "design_assets",
        ["preview_asset_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_box_designs_preview_asset_id_light",
        "box_designs",
        "design_assets",
        ["preview_asset_id_light"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_box_designs_preview_asset_id",
        "box_designs",
        ["preview_asset_id"],
    )
    op.create_index(
        "ix_box_designs_preview_asset_id_light",
        "box_designs",
        ["preview_asset_id_light"],
    )

    op.execute(
        sa.text(
            f"""
            UPDATE box_designs AS bd
            SET preview_asset_id = da.id
            FROM design_assets AS da
            WHERE substring(bd.preview_image_url from '/designs/assets/{_UUID_RE}')
                  = da.id::text
            """
        )
    )
    op.execute(
        sa.text(
            f"""
            UPDATE box_designs AS bd
            SET preview_asset_id_light = da.id
            FROM design_assets AS da
            WHERE substring(
                    bd.theme_config ->> 'preview_image_url_light'
                    from '/designs/assets/{_UUID_RE}'
                  ) = da.id::text
            """
        )
    )


def downgrade() -> None:
    op.drop_index("ix_box_designs_preview_asset_id_light", table_name="box_designs")
    op.drop_index("ix_box_designs_preview_asset_id", table_name="box_designs")
    op.drop_constraint(
        "fk_box_designs_preview_asset_id_light",
        "box_designs",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_box_designs_preview_asset_id",
        "box_designs",
        type_="foreignkey",
    )
    op.drop_column("box_designs", "preview_asset_id_light")
    op.drop_column("box_designs", "preview_asset_id")
