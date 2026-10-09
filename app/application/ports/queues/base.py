"""Порт фоновой очереди задач."""

from abc import ABC, abstractmethod


class BaseTaskQueue(ABC):
    """Контракт адаптера очереди: пробуждение воркера уведомлений."""

    @abstractmethod
    async def kick_notification_dispatch(self) -> None:
        """Сигнализирует воркеру немедленно обработать due ``notification_jobs``."""
