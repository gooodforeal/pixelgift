"""Контракт персистентности задач уведомлений."""

from abc import ABC, abstractmethod
from datetime import datetime
import uuid

from app.domain.entities.notification_jobs import (
    NotificationJob,
    NotificationTemplate,
)
from app.domain.repository.base import BaseRepository


class BaseNotificationJobsRepository(BaseRepository[NotificationJob], ABC):
    """Задачи по боксу/шаблону и захват due-записей воркером."""

    @abstractmethod
    async def get_by_box_and_template(
        self,
        box_id: uuid.UUID,
        template: NotificationTemplate,
    ) -> NotificationJob | None: ...

    @abstractmethod
    async def claim_due(
        self,
        now: datetime,
        *,
        limit: int = 20,
        stale_before: datetime | None = None,
    ) -> list[NotificationJob]: ...
