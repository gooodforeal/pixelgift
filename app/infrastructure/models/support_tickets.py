"""ORM-модель тикетов поддержки."""
import uuid

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.models.base import Base, TimestampMixin


class SupportTicketModel(TimestampMixin, Base):
    """Обращение в поддержку со статусом и вложениями."""

    __tablename__ = "support_tickets"
    __table_args__ = (
        Index("ix_support_tickets_status_created_at", "status", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    contact: Mapped[str] = mapped_column(String(254), nullable=False)
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)

    attachments: Mapped[list["SupportTicketAttachmentModel"]] = relationship(
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="SupportTicketAttachmentModel.created_at",
    )


class SupportTicketAttachmentModel(Base):
    """Вложение тикета (ключ в storage)."""

    __tablename__ = "support_ticket_attachments"
    __table_args__ = (
        Index("ix_support_ticket_attachments_ticket_id", "ticket_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("support_tickets.id", ondelete="CASCADE"),
        nullable=False,
    )
    storage_key: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    ticket: Mapped[SupportTicketModel] = relationship(back_populates="attachments")
