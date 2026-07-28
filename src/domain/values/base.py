from dataclasses import dataclass
from typing import Generic, TypeVar
from abc import ABC


T = TypeVar("T")

@dataclass(frozen=True)
class BaseValueObject(Generic[T], ABC):
    value: T
