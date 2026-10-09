"""Планирование и отправка отложенных уведомлений (email и Telegram)."""

from datetime import datetime, timedelta, timezone
import logging
import uuid

from app.application.services.notifications import (
    NotificationService,
    OwnerTelegramEvent,
)
from app.application.uow.base import BaseUnitOfWork
from app.domain.aggregates.boxes import Box, BoxStatus
from app.domain.entities.notification_jobs import (
    NotificationJob,
    NotificationJobStatus,
    NotificationTemplate,
)

logger = logging.getLogger(__name__)

_TEMPLATE_TELEGRAM_EVENT: dict[NotificationTemplate, OwnerTelegramEvent] = {
    NotificationTemplate.BOX_OPENED: OwnerTelegramEvent.OPENED,
    NotificationTemplate.BOX_PUBLISHED: OwnerTelegramEvent.PUBLISHED,
    NotificationTemplate.BOX_ARCHIVED: OwnerTelegramEvent.ARCHIVED,
    NotificationTemplate.BOX_UNARCHIVED: OwnerTelegramEvent.UNARCHIVED,
}


async def sync_gift_ready_job(uow: BaseUnitOfWork, box: Box) -> None:
    """Синхронизирует job письма получателю на ``activates_at`` при scheduled/active."""
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

    scheduled_at = box.activates_at.value
    if existing is None:
        await uow.notification_jobs.add(
            NotificationJob.create(
                box_id=box.id,
                template=NotificationTemplate.GIFT_READY,
                scheduled_at=scheduled_at,
            )
        )
        return

    if existing.status == NotificationJobStatus.SENT:
        return

    existing.reschedule(scheduled_at)
    await uow.notification_jobs.update(existing)


async def schedule_owner_notification_job(
    uow: BaseUnitOfWork,
    *,
    box_id: uuid.UUID,
    template: NotificationTemplate,
    at: datetime | None = None,
    resend_if_sent: bool = False,
) -> bool:
    """Создаёт или перепланирует job уведомления владельца на момент ``at``.

    Returns:
        True, если job запланирован к (повторной) отправке.
    """
    if template is NotificationTemplate.GIFT_READY:
        raise ValueError("Use sync_gift_ready_job for gift_ready")

    moment = at or datetime.now(timezone.utc)
    existing = await uow.notification_jobs.get_by_box_and_template(box_id, template)

    if existing is None:
        await uow.notification_jobs.add(
            NotificationJob.create(
                box_id=box_id,
                template=template,
                scheduled_at=moment,
            )
        )
        return True

    if existing.status == NotificationJobStatus.SENT and not resend_if_sent:
        return False

    existing.reschedule(moment)
    await uow.notification_jobs.update(existing)
    return True


class DispatchDueNotificationsUseCase:
    """Воркер: забирает due jobs, отправляет письма/Telegram, учитывает retry."""

    def __init__(
        self,
        uow: BaseUnitOfWork,
        notifications: NotificationService,
        *,
        max_attempts: int = 2,
        processing_stale_minutes: int = 10,
    ) -> None:
        self._uow = uow
        self._notifications = notifications
        self._max_attempts = max_attempts
        self._processing_stale_minutes = processing_stale_minutes

    async def execute(self, *, now: datetime | None = None) -> int:
        now = now or datetime.now(timezone.utc)
        stale_before = now - timedelta(minutes=self._processing_stale_minutes)
        dispatched = 0
        while True:
            async with self._uow as uow:
                jobs = await uow.notification_jobs.claim_due(
                    now,
                    limit=1,
                    stale_before=stale_before,
                )
                if not jobs:
                    return dispatched

                job = jobs[0]
                try:
                    sent = await self._dispatch_job(uow, job)
                    if sent:
                        job.mark_sent(now=now)
                        dispatched += 1
                except ValueError as exc:
                    logger.warning(
                        "Notification job %s failed permanently: %s", job.id, exc
                    )
                    job.mark_failed(str(exc))
                except Exception as exc:
                    logger.exception("Failed to dispatch notification job %s", job.id)
                    retried = job.register_failure(
                        str(exc),
                        max_attempts=self._max_attempts,
                        now=now,
                    )
                    if retried:
                        logger.info(
                            "Notification job %s rescheduled (attempt %s/%s) "
                            "next_run_at=%s scheduled_at=%s",
                            job.id,
                            job.attempt_count,
                            self._max_attempts,
                            job.next_run_at.isoformat(),
                            job.scheduled_at.isoformat(),
                        )

                await uow.notification_jobs.update(job)
                await uow.commit()

    async def _dispatch_job(self, uow: BaseUnitOfWork, job: NotificationJob) -> bool:
        box = await uow.boxes.get_by_id(job.box_id)
        if box is None:
            raise ValueError(f"Box not found: {job.box_id}")

        owner = await uow.users.get_by_id(box.owner_id)
        if owner is None:
            raise ValueError(f"Box owner not found: {box.owner_id}")

        if job.template is NotificationTemplate.GIFT_READY:
            if box.status == BoxStatus.ARCHIVED:
                job.cancel()
                return False
            if box.recipient_email is None:
                raise ValueError("Box has no recipient email")
            await self._notifications.notify_gift_ready(box=box, owner=owner)
            return True

        event = _TEMPLATE_TELEGRAM_EVENT.get(job.template)
        if event is None:
            raise ValueError(f"Unknown notification template: {job.template}")

        if job.template is NotificationTemplate.BOX_OPENED:
            if box.first_opened_at is None:
                raise ValueError("Box has not been opened yet")
        elif job.template is NotificationTemplate.BOX_ARCHIVED:
            if box.status != BoxStatus.ARCHIVED:
                job.cancel()
                return False
        elif job.template is NotificationTemplate.BOX_UNARCHIVED:
            if box.status == BoxStatus.ARCHIVED:
                job.cancel()
                return False
        elif job.template is NotificationTemplate.BOX_PUBLISHED:
            if box.status == BoxStatus.DRAFT:
                job.cancel()
                return False

        await self._notifications.notify_owner_telegram(
            box=box,
            owner=owner,
            event=event,
        )
        return True
