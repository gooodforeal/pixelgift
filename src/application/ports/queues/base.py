from abc import ABC, abstractmethod
import uuid


class BaseTaskQueue(ABC):
    @abstractmethod
    async def enqueue_owner_telegram(
        self, box_id: uuid.UUID, event: str
    ) -> None: ...
