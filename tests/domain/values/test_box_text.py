import pytest

from src.domain.exceptions.boxes import (
    BoxMessageEmptyError,
    BoxMessageTooLongError,
    BoxPreviewTitleEmptyError,
    BoxPreviewTitleTooLongError,
    BoxRecipientNameEmptyError,
    BoxRecipientNameSurroundingWhitespaceError,
    BoxRecipientNameTooLongError,
    BoxTitleEmptyError,
    BoxTitleSurroundingWhitespaceError,
    BoxTitleTooLongError,
)
from src.domain.values.box_message import BoxMessage
from src.domain.values.box_preview_title import BoxPreviewTitle
from src.domain.values.box_recipient_name import BoxRecipientName
from src.domain.values.box_title import BoxTitle


class TestBoxTitle:
    def test_valid(self):
        assert BoxTitle("For you").value == "For you"

    def test_max_length(self):
        value = "a" * 30
        assert BoxTitle(value).value == value

    def test_empty(self):
        with pytest.raises(BoxTitleEmptyError):
            BoxTitle("")

    def test_whitespace_only(self):
        with pytest.raises(BoxTitleEmptyError):
            BoxTitle("   ")

    def test_padded(self):
        with pytest.raises(BoxTitleSurroundingWhitespaceError):
            BoxTitle(" title ")

    def test_too_long(self):
        with pytest.raises(BoxTitleTooLongError):
            BoxTitle("a" * 31)


class TestBoxRecipientName:
    def test_valid(self):
        assert BoxRecipientName("Маша").value == "Маша"

    def test_max_length(self):
        value = "a" * 30
        assert BoxRecipientName(value).value == value

    def test_empty(self):
        with pytest.raises(BoxRecipientNameEmptyError):
            BoxRecipientName("")

    def test_whitespace_only(self):
        with pytest.raises(BoxRecipientNameEmptyError):
            BoxRecipientName("   ")

    def test_padded(self):
        with pytest.raises(BoxRecipientNameSurroundingWhitespaceError):
            BoxRecipientName(" name ")

    def test_too_long(self):
        with pytest.raises(BoxRecipientNameTooLongError):
            BoxRecipientName("a" * 31)


class TestBoxPreviewTitle:
    def test_valid(self):
        assert BoxPreviewTitle("Soon").value == "Soon"

    def test_max_length(self):
        value = "a" * 30
        assert BoxPreviewTitle(value).value == value

    def test_empty(self):
        with pytest.raises(BoxPreviewTitleEmptyError):
            BoxPreviewTitle("")

    def test_too_long(self):
        with pytest.raises(BoxPreviewTitleTooLongError):
            BoxPreviewTitle("a" * 31)


class TestBoxMessage:
    def test_valid(self):
        assert BoxMessage("Hello").value == "Hello"

    def test_max_length(self):
        value = "a" * 300
        assert BoxMessage(value).value == value

    def test_empty(self):
        with pytest.raises(BoxMessageEmptyError):
            BoxMessage("")

    def test_too_long(self):
        with pytest.raises(BoxMessageTooLongError):
            BoxMessage("a" * 301)
