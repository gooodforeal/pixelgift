from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import uuid

from src.domain.entities.base import BaseEntity


class NotificationJobStatus(StrEnum):
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationTemplate(StrEnum):
    GIFT_READY = "gift_ready"
    BOX_OPENED = "box_opened"


@dataclass(frozen=False, kw_only=True)
class NotificationJob(BaseEntity):
    box_id: uuid.UUID
    template: NotificationTemplate
    run_at: datetime
    status: NotificationJobStatus = NotificationJobStatus.SCHEDULED
    sent_at: datetime | None = None
    last_error: str | None = None

    def mark_processing(self) -> None:
        self.status = NotificationJobStatus.PROCESSING
        self.last_error = None
        self._touch()

    def mark_sent(self, *, now: datetime | None = None) -> None:
        self.status = NotificationJobStatus.SENT
        self.sent_at = now or datetime.now(timezone.utc)
        self.last_error = None
        self._touch()

    def mark_failed(self, error: str) -> None:
        self.status = NotificationJobStatus.FAILED
        self.last_error = error[:1000]
        self._touch()

    def cancel(self) -> None:
        if self.status == NotificationJobStatus.SENT:
            return
        self.status = NotificationJobStatus.CANCELLED
        self._touch()

    def reschedule(self, run_at: datetime) -> None:
        self.run_at = run_at
        self.status = NotificationJobStatus.SCHEDULED
        self.sent_at = None
        self.last_error = None
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
