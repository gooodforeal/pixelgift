"""Контракт персистентности промокодов."""

from abc import ABC, abstractmethod

from app.domain.entities.promo_codes import PromoCode
from app.domain.repository.base import BaseRepository


class BasePromoCodesRepository(BaseRepository[PromoCode], ABC):
    """CRUD промокодов с постраничным списком."""

    @abstractmethod
    async def get_by_code(self, code: str) -> PromoCode | None: ...

    @abstractmethod
    async def list_all(self) -> list[PromoCode]: ...

    @abstractmethod
    async def list_page(
        self, *, limit: int, offset: int = 0
    ) -> list[PromoCode]: ...

    @abstractmethod
    async def count_all(self) -> int: ...
