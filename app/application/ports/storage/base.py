from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import timedelta


class BaseObjectStorage(ABC):
    @abstractmethod
    async def upload(
        self,
        key: str,
        data: bytes,
        *,
        content_type: str,
    ) -> None: ...

    @abstractmethod
    async def download(self, key: str) -> bytes: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    async def exists(self, key: str) -> bool: ...

    @abstractmethod
    async def generate_presigned_url(
        self,
        key: str,
        *,
        expires_in: timedelta = timedelta(hours=1),
    ) -> str: ...

    async def stream_download(self, key: str) -> AsyncIterator[bytes]:
        yield await self.download(key)
