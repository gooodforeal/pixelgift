"""Отложенная отправка Telegram-уведомлений по событиям бокса."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
import uuid

from app.domain.entities.base import BaseEntity


class NotificationJobStatus(StrEnum):
    """Состояние задачи уведомления в очереди."""

    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationTemplate(StrEnum):
    """Шаблон текста уведомления для конкретного события бокса."""

    GIFT_READY = "gift_ready"
    BOX_OPENED = "box_opened"
    BOX_PUBLISHED = "box_published"
    BOX_ARCHIVED = "box_archived"
    BOX_UNARCHIVED = "box_unarchived"


def _retry_delay_minutes(attempt_count: int) -> int:
    """Экспоненциальная задержка повтора после сбоя: 1, 2, 4, 8, 16, 30… минут."""
    if attempt_count < 1:
        return 1
    return min(30, 2 ** (attempt_count - 1))


@dataclass(frozen=False, kw_only=True)
class NotificationJob(BaseEntity):
    """Задача отправки уведомления с расписанием, попытками и статусом."""

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
        """Создаёт новую задачу с next_run_at, равным scheduled_at."""
        return cls(
            box_id=box_id,
            template=template,
            scheduled_at=scheduled_at,
            next_run_at=scheduled_at,
            status=status,
        )

    def mark_processing(self) -> None:
        """Помечает задачу как выполняющуюся, сбрасывает last_error."""
        self.status = NotificationJobStatus.PROCESSING
        self.last_error = None
        self._touch()

    def mark_sent(self, *, now: datetime | None = None) -> None:
        """Фиксирует успешную отправку и время sent_at."""
        self.status = NotificationJobStatus.SENT
        self.sent_at = now or datetime.now(timezone.utc)
        self.last_error = None
        self._touch()

    def mark_failed(self, error: str) -> None:
        """Окончательный сбой без дальнейших автоматических повторов."""
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
        """Учитывает неудачную попытку отправки.

        Returns:
            True, если задача перепланирована на повтор; False, если исчерпан
            лимит попыток и статус стал failed.
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
        """Отменяет задачу; уже отправленные не меняются."""
        if self.status == NotificationJobStatus.SENT:
            return
        self.status = NotificationJobStatus.CANCELLED
        self._touch()

    def reschedule(self, scheduled_at: datetime) -> None:
        """Сбрасывает расписание и счётчик попыток (например, при смене activates_at)."""
        self.scheduled_at = scheduled_at
        self.next_run_at = scheduled_at
        self.status = NotificationJobStatus.SCHEDULED
        self.sent_at = None
        self.last_error = None
        self.attempt_count = 0
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
