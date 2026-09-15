from datetime import datetime, timezone
import logging
import uuid

from src.application.services.notifications import (
    NotificationService,
    OwnerTelegramEvent,
)
from src.application.uow.base import BaseUnitOfWork
from src.domain.aggregates.boxes import Box, BoxStatus
from src.domain.entities.notification_jobs import (
    NotificationJob,
    NotificationJobStatus,
    NotificationTemplate,
)

logger = logging.getLogger(__name__)


async def sync_gift_ready_job(uow: BaseUnitOfWork, box: Box) -> None:
    existing = await uow.notification_jobs.get_by_box_and_template(
        box.id,
        NotificationTemplate.GIFT_READY,
    )

    if box.status == BoxStatus.ARCHIVED:
        if existing is not None and existing.status in {
            NotificationJobStatus.SCHEDULED,
            NotificationJobStatus.FAILED,
            NotificationJobStatus.PROCESSING,
        }:
            existing.cancel()
            await uow.notification_jobs.update(existing)
        return

    if box.status not in {BoxStatus.SCHEDULED, BoxStatus.ACTIVE}:
        return
    if box.recipient_email is None:
        return

    run_at = box.activates_at.value
    if existing is None:
        await uow.notification_jobs.add(
            NotificationJob(
                box_id=box.id,
                template=NotificationTemplate.GIFT_READY,
                run_at=run_at,
            )
        )
        return

    if existing.status == NotificationJobStatus.SENT:
        return

    existing.reschedule(run_at)
    await uow.notification_jobs.update(existing)


class DispatchDueNotificationsUseCase:
    def __init__(
        self,
        uow: BaseUnitOfWork,
        notifications: NotificationService,
    ) -> None:
        self._uow = uow
        self._notifications = notifications

    async def execute(self, *, now: datetime | None = None) -> int:
        dispatched = 0
        while True:
            async with self._uow as uow:
                jobs = await uow.notification_jobs.claim_due(
                    now or datetime.now(timezone.utc),
                    limit=1,
                )
                if not jobs:
                    return dispatched

                job = jobs[0]
                try:
                    sent = await self._dispatch_job(uow, job)
                    if sent:
                        job.mark_sent()
                        dispatched += 1
                except Exception as exc:
                    logger.exception("Failed to dispatch notification job %s", job.id)
                    job.mark_failed(str(exc))

                await uow.notification_jobs.update(job)
                await uow.commit()

    async def _dispatch_job(self, uow: BaseUnitOfWork, job: NotificationJob) -> bool:
        box = await uow.boxes.get_by_id(job.box_id)
        if box is None:
            raise ValueError(f"Box not found: {job.box_id}")
        if box.status == BoxStatus.ARCHIVED:
            job.cancel()
            return False
        if box.recipient_email is None:
            raise ValueError("Box has no recipient email")

        owner = await uow.users.get_by_id(box.owner_id)
        if owner is None:
            raise ValueError(f"Box owner not found: {box.owner_id}")

        await self._notifications.notify_gift_ready(box=box, owner=owner)
        return True


class NotifyOwnerTelegramUseCase:
    def __init__(
        self,
        uow: BaseUnitOfWork,
        notifications: NotificationService,
    ) -> None:
        self._uow = uow
        self._notifications = notifications

    async def execute(self, *, box_id: uuid.UUID, event: str) -> bool:
        try:
            parsed = OwnerTelegramEvent(event)
        except ValueError:
            logger.warning("Unknown owner telegram event: %s", event)
            return False

        if parsed is OwnerTelegramEvent.OPENED:
            return await self._execute_opened(box_id)

        async with self._uow as uow:
            box = await uow.boxes.get_by_id(box_id)
            if box is None:
                return False
            owner = await uow.users.get_by_id(box.owner_id)
            if owner is None:
                return False

        await self._notifications.notify_owner_telegram(
            box=box, owner=owner, event=parsed
        )
        return True

    async def _execute_opened(self, box_id: uuid.UUID) -> bool:
        async with self._uow as uow:
            box = await uow.boxes.get_by_id(box_id)
            if box is None or box.first_opened_at is None:
                return False

            existing = await uow.notification_jobs.get_by_box_and_template(
                box.id,
                NotificationTemplate.BOX_OPENED,
            )
            if existing is not None and existing.status == NotificationJobStatus.SENT:
                return False

            job = existing or NotificationJob(
                box_id=box.id,
                template=NotificationTemplate.BOX_OPENED,
                run_at=box.first_opened_at,
                status=NotificationJobStatus.PROCESSING,
            )
            if existing is None:
                await uow.notification_jobs.add(job)
            else:
                job.mark_processing()

            owner = await uow.users.get_by_id(box.owner_id)
            if owner is None:
                job.mark_failed(f"Box owner not found: {box.owner_id}")
                await uow.notification_jobs.update(job)
                await uow.commit()
                return False

            try:
                await self._notifications.notify_owner_telegram(
                    box=box,
                    owner=owner,
                    event=OwnerTelegramEvent.OPENED,
                )
                job.mark_sent()
            except Exception as exc:
                logger.exception("Failed to notify owner about opened box %s", box.id)
                job.mark_failed(str(exc))
                await uow.notification_jobs.update(job)
                await uow.commit()
                return False

            await uow.notification_jobs.update(job)
            await uow.commit()
            return True
