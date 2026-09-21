import pytest

from app.domain.exceptions.sort_order import (
    SortOrderNonPositiveError,
    SortOrderNotIntegerError,
)
from app.domain.values.sort_order import SortOrder


class TestSortOrder:
    def test_valid(self):
        assert SortOrder(1).value == 1
        assert SortOrder(42).value == 42

    def test_zero(self):
        with pytest.raises(SortOrderNonPositiveError):
            SortOrder(0)

    def test_negative(self):
        with pytest.raises(SortOrderNonPositiveError):
            SortOrder(-1)

    def test_bool_rejected(self):
        with pytest.raises(SortOrderNotIntegerError):
            SortOrder(True)
