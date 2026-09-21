import uuid

from sqlalchemy import BigInteger, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base, CreatedAtMixin


class DesignAssetModel(CreatedAtMixin, Base):
    __tablename__ = "design_assets"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    storage_key: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(512), nullable=True)
