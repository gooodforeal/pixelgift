import pytest

from app.domain.exceptions.users import (
    TelegramIdNonPositiveError,
    TelegramIdNotNumericError,
    TelegramIdTooLongError,
)
from app.domain.values.telegram_id import TelegramId


class TestTelegramId:
    def test_valid_telegram_id(self):
        telegram_id = TelegramId("1234567890")
        assert telegram_id.value == "1234567890"

    def test_char_telegram_id(self):
        with pytest.raises(TelegramIdNotNumericError):
            TelegramId("not-a-number")

    def test_empty_telegram_id(self):
        with pytest.raises(TelegramIdNotNumericError):
            TelegramId("")

    def test_negative_telegram_id(self):
        with pytest.raises(TelegramIdNonPositiveError):
            TelegramId("-1234567890")

    def test_float_telegram_id(self):
        with pytest.raises(TelegramIdNotNumericError):
            TelegramId("1234567890.1234567890")

    def test_zero_telegram_id(self):
        with pytest.raises(TelegramIdNonPositiveError):
            TelegramId("0")

    def test_long_telegram_id(self):
        with pytest.raises(TelegramIdTooLongError):
            TelegramId("123456789012345678901")
