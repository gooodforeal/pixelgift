import uuid

from sqlalchemy import ForeignKey, Integer, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.models.base import Base, TimestampMixin


class DesignRatingModel(TimestampMixin, Base):
    __tablename__ = "design_ratings"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "design_id",
            name="uq_design_ratings_user_id_design_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    design_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("box_designs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stars: Mapped[int] = mapped_column(Integer, nullable=False)
