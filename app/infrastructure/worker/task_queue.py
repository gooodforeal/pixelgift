"""Адаптер очереди: постановка kick_notification_dispatch в Taskiq."""

from app.application.ports.queues.base import BaseTaskQueue


class TaskiqTaskQueue(BaseTaskQueue):
    """Реализация BaseTaskQueue для немедленного пробуждения воркера уведомлений."""

    async def kick_notification_dispatch(self) -> None:
        from app.infrastructure.worker.tasks import kick_notification_dispatch

        await kick_notification_dispatch.kiq()
