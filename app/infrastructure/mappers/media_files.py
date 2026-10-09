"""Маппинг MediaFile ↔ MediaFileModel."""

from app.domain.entities.media_files import MediaFile, MediaKind
from app.infrastructure.models.media_files import MediaFileModel


def media_file_to_model(entity: MediaFile) -> MediaFileModel:
    return MediaFileModel(
        id=entity.id,
        owner_id=entity.owner_id,
        storage_key=entity.storage_key,
        original_filename=entity.original_filename,
        mime_type=entity.mime_type,
        media_kind=entity.media_kind.value,
        size_bytes=entity.size_bytes,
        duration_ms=entity.duration_ms,
        width=entity.width,
        height=entity.height,
        checksum_sha256=entity.checksum_sha256,
        created_at=entity.created_at,
    )


def media_file_to_entity(model: MediaFileModel) -> MediaFile:
    return MediaFile(
        id=model.id,
        owner_id=model.owner_id,
        storage_key=model.storage_key,
        original_filename=model.original_filename,
        mime_type=model.mime_type,
        media_kind=MediaKind(model.media_kind),
        size_bytes=model.size_bytes,
        duration_ms=model.duration_ms,
        width=model.width,
        height=model.height,
        checksum_sha256=model.checksum_sha256,
        created_at=model.created_at,
        updated_at=model.created_at,
    )


def apply_media_file(entity: MediaFile, model: MediaFileModel) -> None:
    model.owner_id = entity.owner_id
    model.storage_key = entity.storage_key
    model.original_filename = entity.original_filename
    model.mime_type = entity.mime_type
    model.media_kind = entity.media_kind.value
    model.size_bytes = entity.size_bytes
    model.duration_ms = entity.duration_ms
    model.width = entity.width
    model.height = entity.height
    model.checksum_sha256 = entity.checksum_sha256
