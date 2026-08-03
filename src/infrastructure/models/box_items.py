import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.models.base import Base, CreatedAtMixin

if TYPE_CHECKING:
    from src.infrastructure.models.boxes import BoxModel


class BoxItemModel(CreatedAtMixin, Base):
    __tablename__ = "box_items"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    box_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("boxes.id", ondelete="CASCADE"),
        nullable=False,
    )
    media_file_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("media_files.id"),
        nullable=True,
    )
    item_type: Mapped[str] = mapped_column(String(16), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    item_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
    )

    box: Mapped["BoxModel"] = relationship(back_populates="items")
