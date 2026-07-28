import pytest

from src.domain.exceptions.box_items import (
    BoxItemCaptionEmptyError,
    BoxItemCaptionSurroundingWhitespaceError,
    BoxItemCaptionTooLongError,
)
from src.domain.values.box_item_caption import BoxItemCaption


class TestBoxItemCaption:
    def test_valid(self):
        assert BoxItemCaption("Hello").value == "Hello"

    def test_max_length(self):
        value = "a" * 10_000
        assert BoxItemCaption(value).value == value

    def test_empty(self):
        with pytest.raises(BoxItemCaptionEmptyError):
            BoxItemCaption("")

    def test_too_long(self):
        with pytest.raises(BoxItemCaptionTooLongError):
            BoxItemCaption("a" * 10_001)

    def test_padded(self):
        with pytest.raises(BoxItemCaptionSurroundingWhitespaceError):
            BoxItemCaption(" text ")
