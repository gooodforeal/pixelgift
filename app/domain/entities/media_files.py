from dataclasses import dataclass
from enum import StrEnum
import uuid

from app.domain.entities.base import BaseEntity


class MediaKind(StrEnum):
    IMAGE = "image"
    GIF = "gif"
    VIDEO = "video"
    VOICE = "voice"


@dataclass(frozen=False, kw_only=True)
class MediaFile(BaseEntity):
    owner_id: uuid.UUID
    storage_key: str
    mime_type: str
    media_kind: MediaKind
    size_bytes: int
    original_filename: str | None = None
    duration_ms: int | None = None
    width: int | None = None
    height: int | None = None
    checksum_sha256: str | None = None
