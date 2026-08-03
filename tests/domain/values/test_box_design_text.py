import pytest

from src.domain.exceptions.box_designs import (
    BoxDesignDescriptionEmptyError,
    BoxDesignDescriptionTooLongError,
    BoxDesignNameEmptyError,
    BoxDesignNameSurroundingWhitespaceError,
    BoxDesignNameTooLongError,
)
from src.domain.values.box_design_description import BoxDesignDescription
from src.domain.values.box_design_name import BoxDesignName


class TestBoxDesignName:
    def test_valid(self):
        assert BoxDesignName("Romantic Red").value == "Romantic Red"

    def test_max_length(self):
        value = "a" * 15
        assert BoxDesignName(value).value == value

    def test_empty(self):
        with pytest.raises(BoxDesignNameEmptyError):
            BoxDesignName("")

    def test_whitespace_only(self):
        with pytest.raises(BoxDesignNameEmptyError):
            BoxDesignName("   ")

    def test_padded(self):
        with pytest.raises(BoxDesignNameSurroundingWhitespaceError):
            BoxDesignName(" name ")

    def test_too_long(self):
        with pytest.raises(BoxDesignNameTooLongError):
            BoxDesignName("a" * 16)


class TestBoxDesignDescription:
    def test_valid(self):
        assert BoxDesignDescription("Short text").value == "Short text"

    def test_max_length(self):
        value = "a" * 40
        assert BoxDesignDescription(value).value == value

    def test_empty(self):
        with pytest.raises(BoxDesignDescriptionEmptyError):
            BoxDesignDescription("")

    def test_too_long(self):
        with pytest.raises(BoxDesignDescriptionTooLongError):
            BoxDesignDescription("a" * 41)
