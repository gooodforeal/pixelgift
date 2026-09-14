from datetime import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.notification_jobs import (
    NotificationJob,
    NotificationJobStatus,
    NotificationTemplate,
)
from src.domain.repository.notification_jobs import BaseNotificationJobsRepository
from src.infrastructure.mappers.notification_jobs import (
    apply_notification_job,
    notification_job_to_entity,
    notification_job_to_model,
)
from src.infrastructure.models.notification_jobs import NotificationJobModel


class SqlAlchemyNotificationJobsRepository(BaseNotificationJobsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entity: NotificationJob) -> None:
        self._session.add(notification_job_to_model(entity))

    async def get_by_id(self, id_: uuid.UUID) -> NotificationJob | None:
        model = await self._session.get(NotificationJobModel, id_)
        return notification_job_to_entity(model) if model is not None else None

    async def update(self, entity: NotificationJob) -> NotificationJob:
        model = await self._session.get(NotificationJobModel, entity.id)
        if model is None:
            raise ValueError(f"Notification job not found: {entity.id}")
        apply_notification_job(entity, model)
        await self._session.flush()
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        model = await self._session.get(NotificationJobModel, id_)
        if model is not None:
            await self._session.delete(model)

    async def get_by_box_and_template(
        self,
        box_id: uuid.UUID,
        template: NotificationTemplate,
    ) -> NotificationJob | None:
        result = await self._session.execute(
            select(NotificationJobModel).where(
                NotificationJobModel.box_id == box_id,
                NotificationJobModel.template == template.value,
            )
        )
        model = result.scalar_one_or_none()
        return notification_job_to_entity(model) if model is not None else None

    async def claim_due(
        self,
        now: datetime,
        *,
        limit: int = 20,
    ) -> list[NotificationJob]:
        result = await self._session.execute(
            select(NotificationJobModel)
            .where(
                NotificationJobModel.status == NotificationJobStatus.SCHEDULED.value,
                NotificationJobModel.run_at <= now,
            )
            .order_by(NotificationJobModel.run_at.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        entities: list[NotificationJob] = []
        for model in result.scalars().all():
            entity = notification_job_to_entity(model)
            entity.mark_processing()
            apply_notification_job(entity, model)
            entities.append(entity)
        await self._session.flush()
        return entities
