from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class MediaContent:
    data: bytes
    mime_type: str
    filename: str | None = None
