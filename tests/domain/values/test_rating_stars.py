from app.domain.exceptions.design_ratings import (
    DesignRatingStarsNotIntegerError,
    DesignRatingStarsOutOfRangeError,
)
from app.domain.values.rating_stars import RatingStars
import pytest


class TestRatingStars:
    def test_valid_bounds(self):
        assert RatingStars(1).value == 1
        assert RatingStars(5).value == 5

    def test_out_of_range(self):
        with pytest.raises(DesignRatingStarsOutOfRangeError):
            RatingStars(0)
        with pytest.raises(DesignRatingStarsOutOfRangeError):
            RatingStars(6)

    def test_not_integer(self):
        with pytest.raises(DesignRatingStarsNotIntegerError):
            RatingStars(True)  # type: ignore[arg-type]
        with pytest.raises(DesignRatingStarsNotIntegerError):
            RatingStars(3.5)  # type: ignore[arg-type]
