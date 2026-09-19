"""add support tickets

Revision ID: l2c5e8a1b4d7
Revises: k1b4d7f0a3c6
Create Date: 2026-09-19 23:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "l2c5e8a1b4d7"
down_revision: Union[str, Sequence[str], None] = "k1b4d7f0a3c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "support_tickets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("contact", sa.String(length=254), nullable=False),
        sa.Column("subject", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_support_tickets_status_created_at",
        "support_tickets",
        ["status", "created_at"],
    )

    op.create_table(
        "support_ticket_attachments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("ticket_id", sa.Uuid(), nullable=False),
        sa.Column("storage_key", sa.Text(), nullable=False),
        sa.Column("mime_type", sa.String(length=128), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["ticket_id"], ["support_tickets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_support_ticket_attachments_ticket_id",
        "support_ticket_attachments",
        ["ticket_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_support_ticket_attachments_ticket_id",
        table_name="support_ticket_attachments",
    )
    op.drop_table("support_ticket_attachments")
    op.drop_index("ix_support_tickets_status_created_at", table_name="support_tickets")
    op.drop_table("support_tickets")
