"""Базовые Pydantic-схемы ответов API."""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class BaseResponseSchema(BaseModel, Generic[T]):
    """Обёртка ответа: текстовое сообщение и полезная нагрузка `result`."""

    message: str
    result: T
