"""Команды обращений в поддержку."""

from dataclasses import dataclass
import uuid

from app.domain.entities.support_tickets import SupportTicketStatus


@dataclass(frozen=True, kw_only=True)
class CreateSupportTicketCommand:
    """Новое обращение с опциональными изображениями."""

    contact: str
    subject: str
    description: str
    files: tuple["SupportAttachmentUpload", ...] = ()


@dataclass(frozen=True, kw_only=True)
class SupportAttachmentUpload:
    """Вложение при создании тикета (до загрузки в storage)."""

    data: bytes
    mime_type: str
    original_filename: str | None = None


@dataclass(frozen=True, kw_only=True)
class UpdateSupportTicketStatusCommand:
    """Смена статуса тикета (админ)."""

    ticket_id: uuid.UUID
    status: SupportTicketStatus
