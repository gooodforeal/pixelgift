from abc import ABC, abstractmethod
import uuid


class BaseTaskQueue(ABC):
    @abstractmethod
    async def enqueue_box_opened(self, box_id: uuid.UUID) -> None: ...
