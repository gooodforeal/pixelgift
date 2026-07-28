from datetime import datetime, timezone
import uuid

from src.application.ports.storage.base import BaseObjectStorage
from src.application.uow.base import BaseUnitOfWork
from src.domain.entities.media_files import MediaFile, MediaKind


_MIME_TO_KIND: dict[str, MediaKind] = {
    "image/jpeg": MediaKind.IMAGE,
    "image/png": MediaKind.IMAGE,
    "image/webp": MediaKind.IMAGE,
    "image/gif": MediaKind.GIF,
    "video/mp4": MediaKind.VIDEO,
    "video/webm": MediaKind.VIDEO,
    "audio/mpeg": MediaKind.VOICE,
    "audio/ogg": MediaKind.VOICE,
    "audio/webm": MediaKind.VOICE,
}


class UploadMediaUseCase:
    def __init__(self, uow: BaseUnitOfWork, storage: BaseObjectStorage) -> None:
        self._uow = uow
        self._storage = storage

    async def execute(
        self,
        *,
        owner_id: uuid.UUID,
        data: bytes,
        content_type: str,
        original_filename: str | None = None,
    ) -> MediaFile:
        media_kind = _MIME_TO_KIND.get(content_type, MediaKind.IMAGE)
        media_id = uuid.uuid4()
        extension = _extension(original_filename, content_type)
        storage_key = f"users/{owner_id}/{media_id}{extension}"

        await self._storage.upload(storage_key, data, content_type=content_type)

        media = MediaFile(
            id=media_id,
            owner_id=owner_id,
            storage_key=storage_key,
            mime_type=content_type,
            media_kind=media_kind,
            size_bytes=len(data),
            original_filename=original_filename,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        async with self._uow as uow:
            await uow.media_files.add(media)
            await uow.commit()
        return media


def _extension(filename: str | None, content_type: str) -> str:
    if filename and "." in filename:
        return "." + filename.rsplit(".", 1)[-1].lower()
    mapping = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
        "video/mp4": ".mp4",
        "video/webm": ".webm",
        "audio/mpeg": ".mp3",
        "audio/ogg": ".ogg",
        "audio/webm": ".webm",
    }
    return mapping.get(content_type, ".bin")
