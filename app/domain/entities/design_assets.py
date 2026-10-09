"""Статический ассет дизайна (превью, тема) в хранилище."""

from dataclasses import dataclass

from app.domain.entities.base import BaseEntity


@dataclass(frozen=False, kw_only=True)
class DesignAsset(BaseEntity):
    """Файл ассета без привязки к конкретному боксу."""

    storage_key: str
    mime_type: str
    size_bytes: int
    original_filename: str | None = None
