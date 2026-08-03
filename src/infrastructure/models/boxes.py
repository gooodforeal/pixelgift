import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.infrastructure.models.box_items import BoxItemModel


class BoxModel(TimestampMixin, Base):
    __tablename__ = "boxes"
    __table_args__ = (
        Index("ix_boxes_owner_id_created_at", "owner_id", "created_at"),
        Index("ix_boxes_status_activates_at", "status", "activates_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=False,
    )
    design_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("box_designs.id"),
        nullable=False,
    )
    public_slug: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(30), nullable=False)
    recipient_name: Mapped[str] = mapped_column(String(30), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    preview_title: Mapped[str | None] = mapped_column(String(30), nullable=True)
    preview_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    activates_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="UTC")
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    first_opened_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    items: Mapped[list["BoxItemModel"]] = relationship(
        back_populates="box",
        cascade="all, delete-orphan",
        order_by="BoxItemModel.sort_order",
    )
