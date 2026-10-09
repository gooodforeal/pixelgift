"""Схема ошибок API."""

from app.presentation.schemas.base import BaseResponseSchema


class ErrorResponseSchema(BaseResponseSchema[None]):
    """Ответ об ошибке без поля result."""

    result: None = None
