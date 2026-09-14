from abc import ABC, abstractmethod
from datetime import datetime
import uuid

from src.domain.entities.notification_jobs import (
    NotificationJob,
    NotificationTemplate,
)
from src.domain.repository.base import BaseRepository


class BaseNotificationJobsRepository(BaseRepository[NotificationJob], ABC):
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
    ) -> list[NotificationJob]: ...
