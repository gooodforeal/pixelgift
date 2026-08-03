from dataclasses import dataclass

from src.domain.entities.base import BaseEntity


@dataclass(frozen=False, kw_only=True)
class DesignAsset(BaseEntity):
    storage_key: str
    mime_type: str
    size_bytes: int
    original_filename: str | None = None
