import pytest

from src.domain.exceptions.boxes import (
    BoxRecipientEmailInvalidError,
    BoxRecipientEmailSurroundingWhitespaceError,
)
from src.domain.values.box_recipient_email import BoxRecipientEmail


class TestBoxRecipientEmail:
    def test_valid_email(self):
        email = BoxRecipientEmail("masha@example.com")
        assert email.value == "masha@example.com"

    def test_rejects_whitespace(self):
        with pytest.raises(BoxRecipientEmailSurroundingWhitespaceError):
            BoxRecipientEmail(" masha@example.com ")

    def test_rejects_invalid(self):
        with pytest.raises(BoxRecipientEmailInvalidError):
            BoxRecipientEmail("not-an-email")

    def test_rejects_empty(self):
        with pytest.raises(BoxRecipientEmailInvalidError):
            BoxRecipientEmail("")
