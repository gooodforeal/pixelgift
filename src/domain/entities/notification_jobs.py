from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
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
    BOX_PUBLISHED = "box_published"
    BOX_ARCHIVED = "box_archived"
    BOX_UNARCHIVED = "box_unarchived"


def _retry_delay_minutes(attempt_count: int) -> int:
    """Exponential backoff after failed attempts: 1, 2, 4, 8, 16, 30… minutes."""
    if attempt_count < 1:
        return 1
    return min(30, 2 ** (attempt_count - 1))


@dataclass(frozen=False, kw_only=True)
class NotificationJob(BaseEntity):
    box_id: uuid.UUID
    template: NotificationTemplate
    scheduled_at: datetime
    next_run_at: datetime
    status: NotificationJobStatus = NotificationJobStatus.SCHEDULED
    sent_at: datetime | None = None
    last_error: str | None = None
    attempt_count: int = 0

    @classmethod
    def create(
        cls,
        *,
        box_id: uuid.UUID,
        template: NotificationTemplate,
        scheduled_at: datetime,
        status: NotificationJobStatus = NotificationJobStatus.SCHEDULED,
    ) -> "NotificationJob":
        return cls(
            box_id=box_id,
            template=template,
            scheduled_at=scheduled_at,
            next_run_at=scheduled_at,
            status=status,
        )

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
        """Terminal failure without further automatic retries."""
        self.status = NotificationJobStatus.FAILED
        self.last_error = error[:1000]
        self._touch()

    def register_failure(
        self,
        error: str,
        *,
        max_attempts: int,
        now: datetime | None = None,
    ) -> bool:
        """
        Record a failed send attempt.

        Returns True if the job was rescheduled for retry, False if it became
        permanently failed (attempt_count reached max_attempts).
        """
        now = now or datetime.now(timezone.utc)
        attempts_limit = max(1, max_attempts)
        self.attempt_count += 1
        self.last_error = error[:1000]
        self.sent_at = None

        if self.attempt_count < attempts_limit:
            delay = timedelta(minutes=_retry_delay_minutes(self.attempt_count))
            self.next_run_at = now + delay
            self.status = NotificationJobStatus.SCHEDULED
            self._touch()
            return True

        self.status = NotificationJobStatus.FAILED
        self._touch()
        return False

    def cancel(self) -> None:
        if self.status == NotificationJobStatus.SENT:
            return
        self.status = NotificationJobStatus.CANCELLED
        self._touch()

    def reschedule(self, scheduled_at: datetime) -> None:
        """Reset to a new original plan (e.g. box activation time changed)."""
        self.scheduled_at = scheduled_at
        self.next_run_at = scheduled_at
        self.status = NotificationJobStatus.SCHEDULED
        self.sent_at = None
        self.last_error = None
        self.attempt_count = 0
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
