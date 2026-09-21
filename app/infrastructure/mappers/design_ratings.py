from app.domain.entities.design_ratings import DesignRating
from app.domain.values.rating_stars import RatingStars
from app.infrastructure.models.design_ratings import DesignRatingModel


def design_rating_to_model(entity: DesignRating) -> DesignRatingModel:
    return DesignRatingModel(
        id=entity.id,
        user_id=entity.user_id,
        design_id=entity.design_id,
        stars=entity.stars.value,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def design_rating_to_entity(model: DesignRatingModel) -> DesignRating:
    return DesignRating(
        id=model.id,
        user_id=model.user_id,
        design_id=model.design_id,
        stars=RatingStars(model.stars),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def apply_design_rating(entity: DesignRating, model: DesignRatingModel) -> None:
    model.user_id = entity.user_id
    model.design_id = entity.design_id
    model.stars = entity.stars.value
    model.updated_at = entity.updated_at
