from app.domain.exceptions.base import BaseException
import uuid


class MediaFileNotFoundError(BaseException):
    status_code = 404

    def __init__(self, media_file_id: uuid.UUID) -> None:
        self.media_file_id = media_file_id
        super().__init__(f"Media file not found: {media_file_id}")


class MediaFileAccessDeniedError(BaseException):
    status_code = 403

    def __init__(self, media_file_id: uuid.UUID, actor_id: uuid.UUID) -> None:
        self.media_file_id = media_file_id
        self.actor_id = actor_id
        super().__init__(
            f"Actor {actor_id} cannot use media file {media_file_id}"
        )


class UnsupportedMediaTypeError(BaseException):
    def __init__(self, content_type: str, filename: str | None = None) -> None:
        self.content_type = content_type
        self.filename = filename
        detail = f"Unsupported media type: {content_type!r}"
        if filename:
            detail = f"{detail} (file={filename!r})"
        super().__init__(detail)
