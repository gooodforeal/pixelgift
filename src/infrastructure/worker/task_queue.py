from src.application.ports.queues.base import BaseTaskQueue


class TaskiqTaskQueue(BaseTaskQueue):
    async def kick_notification_dispatch(self) -> None:
        from src.infrastructure.worker.tasks import kick_notification_dispatch

        await kick_notification_dispatch.kiq()
