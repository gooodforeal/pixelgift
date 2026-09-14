import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.models.base import Base, TimestampMixin


class NotificationJobModel(TimestampMixin, Base):
    __tablename__ = "notification_jobs"
    __table_args__ = (
        UniqueConstraint(
            "box_id",
            "template",
            name="uq_notification_jobs_box_id_template",
        ),
        Index("ix_notification_jobs_status_run_at", "status", "run_at"),
    )

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
    template: Mapped[str] = mapped_column(String(32), nullable=False)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
