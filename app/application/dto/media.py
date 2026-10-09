"""DTO отдачи бинарного медиа HTTP-слоем."""

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class MediaContent:
    """Тело файла и метаданные для Content-Type / Content-Disposition."""

    data: bytes
    mime_type: str
    filename: str | None = None
