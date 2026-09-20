import uuid

from src.application.ports.queues.base import BaseTaskQueue


class TaskiqTaskQueue(BaseTaskQueue):
    async def enqueue_owner_telegram(self, box_id: uuid.UUID, event: str) -> None:
        from src.infrastructure.worker.tasks import notify_owner_telegram

        await notify_owner_telegram.kiq(str(box_id), event)
