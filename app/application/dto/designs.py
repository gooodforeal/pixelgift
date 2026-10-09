"""Представления каталога тем оформления боксов."""

from dataclasses import dataclass
import uuid

from app.domain.entities.box_designs import BoxDesign


@dataclass(frozen=True, slots=True)
class BoxDesignWithRating:
    """Активный дизайн с агрегированным рейтингом и оценкой текущего пользователя."""

    design: BoxDesign
    rating_avg: float
    rating_count: int
    my_rating: int | None = None


@dataclass(frozen=True, slots=True)
class DesignRatingResult:
    """Результат выставления звёзд после сохранения оценки."""

    design_id: uuid.UUID
    stars: int
    rating_avg: float
    rating_count: int
