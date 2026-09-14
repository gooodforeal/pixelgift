import uuid

from src.application.ports.task_queue import BaseTaskQueue


class TaskiqTaskQueue(BaseTaskQueue):
    async def enqueue_box_opened(self, box_id: uuid.UUID) -> None:
        from src.infrastructure.worker.tasks import notify_box_opened

        await notify_box_opened.kiq(str(box_id))
