from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class BaseResponseSchema(BaseModel, Generic[T]):
    message: str
    result: T
