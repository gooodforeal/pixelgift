"""Порт объектного хранилища (S3, MinIO, локальный диск)."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import timedelta


class BaseObjectStorage(ABC):
    """Контракт адаптера блочного хранилища по ключам.

    Use case'ы загружают медиа, аватары, вложения поддержки и скачивают
    содержимое для отдачи клиенту или публичной странице бокса.
    """

    @abstractmethod
    async def upload(
        self,
        key: str,
        data: bytes,
        *,
        content_type: str,
    ) -> None:
        """Сохраняет объект по ключу с указанным MIME-типом."""

    @abstractmethod
    async def download(self, key: str) -> bytes:
        """Загружает объект целиком в память."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Удаляет объект по ключу (если существует)."""

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Проверяет наличие объекта по ключу."""

    @abstractmethod
    async def generate_presigned_url(
        self,
        key: str,
        *,
        expires_in: timedelta = timedelta(hours=1),
    ) -> str:
        """Возвращает временную URL для прямого доступа к объекту."""

    async def stream_download(self, key: str) -> AsyncIterator[bytes]:
        """Потоковая отдача; по умолчанию — один chunk из ``download``."""
        yield await self.download(key)
