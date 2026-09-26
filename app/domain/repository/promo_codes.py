from abc import ABC, abstractmethod

from app.domain.entities.promo_codes import PromoCode
from app.domain.repository.base import BaseRepository


class BasePromoCodesRepository(BaseRepository[PromoCode], ABC):
    @abstractmethod
    async def get_by_code(self, code: str) -> PromoCode | None: ...

    @abstractmethod
    async def list_all(self) -> list[PromoCode]: ...
