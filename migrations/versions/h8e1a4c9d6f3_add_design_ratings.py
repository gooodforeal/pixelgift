"""add design_ratings table

Revision ID: h8e1a4c9d6f3
Revises: g7d0f3b8c5e2
Create Date: 2026-08-08 13:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "h8e1a4c9d6f3"
down_revision: Union[str, Sequence[str], None] = "g7d0f3b8c5e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "design_ratings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("design_id", sa.Uuid(), nullable=False),
        sa.Column("stars", sa.Integer(), nullable=False),
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
            "stars >= 1 AND stars <= 5",
            name="ck_design_ratings_stars_range",
        ),
        sa.ForeignKeyConstraint(
            ["design_id"],
            ["box_designs.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "design_id",
            name="uq_design_ratings_user_id_design_id",
        ),
    )
    op.create_index(
        op.f("ix_design_ratings_design_id"),
        "design_ratings",
        ["design_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_design_ratings_user_id"),
        "design_ratings",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_design_ratings_user_id"), table_name="design_ratings")
    op.drop_index(op.f("ix_design_ratings_design_id"), table_name="design_ratings")
    op.drop_table("design_ratings")
