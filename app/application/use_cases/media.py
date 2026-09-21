from datetime import datetime, timezone
import uuid

from app.application.dto.media import MediaContent
from app.application.ports.storage.base import BaseObjectStorage
from app.application.uow.base import BaseUnitOfWork
from app.domain.entities.media_files import MediaFile, MediaKind
from app.domain.exceptions.media_files import (
    MediaFileAccessDeniedError,
    MediaFileNotFoundError,
    UnsupportedMediaTypeError,
)


_MIME_ALIASES: dict[str, str] = {
    "audio/mp3": "audio/mpeg",
    "audio/x-mp3": "audio/mpeg",
    "audio/mpeg3": "audio/mpeg",
    "audio/x-mpeg": "audio/mpeg",
    "audio/x-ogg": "audio/ogg",
    "application/ogg": "audio/ogg",
    "audio/vorbis": "audio/ogg",
    "audio/opus": "audio/ogg",
    "audio/x-m4a": "audio/mp4",
    "audio/m4a": "audio/mp4",
    "audio/aac": "audio/mp4",
    "video/x-mov": "video/quicktime",
    "application/x-quicktimeplayer": "video/quicktime",
}

_MIME_TO_KIND: dict[str, MediaKind] = {
    "image/jpeg": MediaKind.IMAGE,
    "image/png": MediaKind.IMAGE,
    "image/webp": MediaKind.IMAGE,
    "image/gif": MediaKind.GIF,
    "video/mp4": MediaKind.VIDEO,
    "video/webm": MediaKind.VIDEO,
    "video/quicktime": MediaKind.VIDEO,
    "audio/mpeg": MediaKind.VOICE,
    "audio/ogg": MediaKind.VOICE,
    "audio/webm": MediaKind.VOICE,
    "audio/mp4": MediaKind.VOICE,
    "audio/wav": MediaKind.VOICE,
    "audio/x-wav": MediaKind.VOICE,
    "audio/wave": MediaKind.VOICE,
}

_EXT_TO_KIND: dict[str, MediaKind] = {
    ".jpg": MediaKind.IMAGE,
    ".jpeg": MediaKind.IMAGE,
    ".png": MediaKind.IMAGE,
    ".webp": MediaKind.IMAGE,
    ".gif": MediaKind.GIF,
    ".mp4": MediaKind.VIDEO,
    ".webm": MediaKind.VIDEO,
    ".mov": MediaKind.VIDEO,
    ".mp3": MediaKind.VOICE,
    ".ogg": MediaKind.VOICE,
    ".oga": MediaKind.VOICE,
    ".opus": MediaKind.VOICE,
    ".m4a": MediaKind.VOICE,
    ".aac": MediaKind.VOICE,
    ".wav": MediaKind.VOICE,
}

_EXT_TO_MIME: dict[str, str] = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".mov": "video/quicktime",
    ".mp3": "audio/mpeg",
    ".ogg": "audio/ogg",
    ".oga": "audio/ogg",
    ".opus": "audio/ogg",
    ".m4a": "audio/mp4",
    ".aac": "audio/mp4",
    ".wav": "audio/wav",
}

_KIND_TO_DEFAULT_MIME: dict[MediaKind, str] = {
    MediaKind.IMAGE: "image/jpeg",
    MediaKind.GIF: "image/gif",
    MediaKind.VIDEO: "video/mp4",
    MediaKind.VOICE: "audio/mpeg",
}


def resolve_media_kind(
    content_type: str,
    original_filename: str | None = None,
    *,
    preferred_kind: MediaKind | None = None,
) -> tuple[MediaKind, str]:
    """Return (media_kind, normalized_mime_type)."""
    mime = _normalize_mime(content_type)
    kind_from_mime = _MIME_TO_KIND.get(mime) if mime else None
    ext = _file_extension(original_filename)
    kind_from_ext = _EXT_TO_KIND.get(ext) if ext else None

    if preferred_kind is not None:
        if kind_from_mime is not None and kind_from_mime != preferred_kind:
            webm_flexible = (
                preferred_kind in {MediaKind.VIDEO, MediaKind.VOICE}
                and kind_from_mime in {MediaKind.VIDEO, MediaKind.VOICE}
                and mime.endswith("/webm")
            )
            if not webm_flexible:
                raise UnsupportedMediaTypeError(content_type, original_filename)
        elif (
            kind_from_ext is not None
            and kind_from_ext != preferred_kind
            and not (
                ext == ".webm"
                and preferred_kind in {MediaKind.VIDEO, MediaKind.VOICE}
            )
        ):
            raise UnsupportedMediaTypeError(content_type, original_filename)

        resolved_mime = (
            mime
            or _EXT_TO_MIME.get(ext)
            or _KIND_TO_DEFAULT_MIME[preferred_kind]
        )
        if preferred_kind == MediaKind.VOICE and resolved_mime == "video/webm":
            resolved_mime = "audio/webm"
        if preferred_kind == MediaKind.VIDEO and resolved_mime == "audio/webm":
            resolved_mime = "video/webm"
        return preferred_kind, resolved_mime

    if kind_from_mime is not None:
        return kind_from_mime, mime

    if kind_from_ext is not None:
        return kind_from_ext, _EXT_TO_MIME.get(ext, mime or "application/octet-stream")

    raise UnsupportedMediaTypeError(content_type, original_filename)


def _normalize_mime(content_type: str) -> str:
    mime = (content_type or "").split(";", 1)[0].strip().lower()
    if not mime or mime == "application/octet-stream":
        return ""
    return _MIME_ALIASES.get(mime, mime)


def _file_extension(filename: str | None) -> str:
    if not filename or "." not in filename:
        return ""
    return "." + filename.rsplit(".", 1)[-1].lower()


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
        preferred_kind: MediaKind | None = None,
    ) -> MediaFile:
        media_kind, mime_type = resolve_media_kind(
            content_type,
            original_filename,
            preferred_kind=preferred_kind,
        )
        media_id = uuid.uuid4()
        extension = _extension(original_filename, mime_type)
        storage_key = f"users/{owner_id}/{media_id}{extension}"

        await self._storage.upload(storage_key, data, content_type=mime_type)

        media = MediaFile(
            id=media_id,
            owner_id=owner_id,
            storage_key=storage_key,
            mime_type=mime_type,
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


class GetOwnMediaContentUseCase:
    """Streams a media file back to its owner (used for editor previews)."""

    def __init__(self, uow: BaseUnitOfWork, storage: BaseObjectStorage) -> None:
        self._uow = uow
        self._storage = storage

    async def execute(
        self,
        *,
        media_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> MediaContent:
        async with self._uow as uow:
            media = await uow.media_files.get_by_id(media_id)
            if media is None:
                raise MediaFileNotFoundError(media_id)
            if media.owner_id != actor_id:
                raise MediaFileAccessDeniedError(media_id, actor_id)

        data = await self._storage.download(media.storage_key)
        return MediaContent(
            data=data,
            mime_type=media.mime_type,
            filename=media.original_filename,
        )


def _extension(filename: str | None, content_type: str) -> str:
    ext = _file_extension(filename)
    if ext:
        return ext
    mapping = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
        "video/mp4": ".mp4",
        "video/webm": ".webm",
        "video/quicktime": ".mov",
        "audio/mpeg": ".mp3",
        "audio/ogg": ".ogg",
        "audio/webm": ".webm",
        "audio/mp4": ".m4a",
        "audio/wav": ".wav",
    }
    return mapping.get(content_type, ".bin")
