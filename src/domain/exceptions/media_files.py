from src.domain.exceptions.base import BaseException
import uuid


class MediaFileNotFoundError(BaseException):
    def __init__(self, media_file_id: uuid.UUID) -> None:
        self.media_file_id = media_file_id
        super().__init__(f"Media file not found: {media_file_id}")


class MediaFileAccessDeniedError(BaseException):
    def __init__(self, media_file_id: uuid.UUID, actor_id: uuid.UUID) -> None:
        self.media_file_id = media_file_id
        self.actor_id = actor_id
        super().__init__(
            f"Actor {actor_id} cannot use media file {media_file_id}"
        )
