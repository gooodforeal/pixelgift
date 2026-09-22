import uuid

from app.domain.exceptions.base import BaseException


class DesignRatingError(BaseException):
    """Базовая ошибка рейтинга дизайна."""


class DesignRatingStarsNotIntegerError(DesignRatingError):
    def __init__(self, stars: object) -> None:
        self.stars = stars
        super().__init__(f"Rating stars must be an integer, got {stars!r}")


class DesignRatingStarsOutOfRangeError(DesignRatingError):
    def __init__(self, stars: int) -> None:
        self.stars = stars
        super().__init__(f"Rating stars must be between 1 and 5, got {stars}")


class DesignAlreadyRatedError(DesignRatingError):
    status_code = 409

    def __init__(self, design_id: uuid.UUID, user_id: uuid.UUID) -> None:
        self.design_id = design_id
        self.user_id = user_id
        super().__init__(
            f"User {user_id} has already rated design {design_id}"
        )
