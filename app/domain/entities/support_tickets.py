from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
import uuid

from app.domain.entities.base import BaseEntity


class SupportTicketStatus(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass(frozen=False, kw_only=True)
class SupportTicketAttachment(BaseEntity):
    ticket_id: uuid.UUID
    storage_key: str
    mime_type: str
    size_bytes: int
    original_filename: str | None = None


@dataclass(frozen=False, kw_only=True)
class SupportTicket(BaseEntity):
    contact: str
    subject: str
    description: str
    status: SupportTicketStatus = SupportTicketStatus.NEW
    attachments: list[SupportTicketAttachment] = field(default_factory=list)

    def set_status(self, status: SupportTicketStatus) -> None:
        self.status = status
        self.updated_at = datetime.now(timezone.utc)
