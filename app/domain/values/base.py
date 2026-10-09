"""Базовый неизменяемый объект-значение с типизированным полем value."""

from dataclasses import dataclass
from typing import Generic, TypeVar
from abc import ABC


T = TypeVar("T")


@dataclass(frozen=True)
class BaseValueObject(Generic[T], ABC):
    """Обёртка над примитивом с инвариантами, проверяемыми в наследниках."""

    value: T
