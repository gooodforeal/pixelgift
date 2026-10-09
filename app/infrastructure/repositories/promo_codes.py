"""SQLAlchemy-репозиторий промокодов."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.promo_codes import PromoCode
from app.domain.repository.promo_codes import BasePromoCodesRepository
from app.infrastructure.mappers.promo_codes import (
    apply_promo_code,
    promo_code_to_entity,
    promo_code_to_model,
)
from app.infrastructure.models.promo_codes import PromoCodeModel


class SqlAlchemyPromoCodesRepository(BasePromoCodesRepository):
    """SQLAlchemy-репозиторий промокодов; пагинация list_page."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entity: PromoCode) -> None:
        self._session.add(promo_code_to_model(entity))

    async def get_by_id(self, id_: uuid.UUID) -> PromoCode | None:
        model = await self._session.get(PromoCodeModel, id_)
        return promo_code_to_entity(model) if model is not None else None

    async def update(self, entity: PromoCode) -> PromoCode:
        model = await self._session.get(PromoCodeModel, entity.id)
        if model is None:
            raise ValueError(f"PromoCode not found: {entity.id}")
        apply_promo_code(entity, model)
        await self._session.flush()
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        model = await self._session.get(PromoCodeModel, id_)
        if model is not None:
            await self._session.delete(model)

    async def get_by_code(self, code: str) -> PromoCode | None:
        result = await self._session.execute(
            select(PromoCodeModel).where(PromoCodeModel.code == code)
        )
        model = result.scalar_one_or_none()
        return promo_code_to_entity(model) if model is not None else None

    async def list_all(self) -> list[PromoCode]:
        result = await self._session.execute(
            select(PromoCodeModel).order_by(PromoCodeModel.created_at.desc())
        )
        return [promo_code_to_entity(m) for m in result.scalars().all()]

    async def list_page(
        self, *, limit: int, offset: int = 0
    ) -> list[PromoCode]:
        result = await self._session.execute(
            select(PromoCodeModel)
            .order_by(PromoCodeModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return [promo_code_to_entity(m) for m in result.scalars().all()]

    async def count_all(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(PromoCodeModel)
        )
        return int(result.scalar_one())
