from dataclasses import dataclass
import uuid

from src.domain.entities.box_designs import BoxDesign


@dataclass(frozen=True, slots=True)
class BoxDesignWithRating:
    design: BoxDesign
    rating_avg: float
    rating_count: int
    my_rating: int | None = None


@dataclass(frozen=True, slots=True)
class DesignRatingResult:
    design_id: uuid.UUID
    stars: int
    rating_avg: float
    rating_count: int
