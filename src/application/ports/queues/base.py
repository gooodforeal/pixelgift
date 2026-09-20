from abc import ABC, abstractmethod


class BaseTaskQueue(ABC):
    @abstractmethod
    async def kick_notification_dispatch(self) -> None:
        """Wake the worker to process due notification_jobs immediately."""
