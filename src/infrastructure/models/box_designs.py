import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.models.base import Base, TimestampMixin


class BoxDesignModel(TimestampMixin, Base):
    __tablename__ = "box_designs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    preview_image_url: Mapped[str] = mapped_column(Text, nullable=False)
    preview_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("design_assets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    preview_asset_id_light: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("design_assets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    theme_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
