import pytest

from src.domain.values.telegram_id import TelegramId
from src.domain.exceptions.users import TelegramIdInvalidError


class TestTelegramId:
    def test_valid_telegram_id(self):
        telegram_id = TelegramId("1234567890")
        assert telegram_id.value == "1234567890"

    def test_char_telegram_id(self):
        with pytest.raises(TelegramIdInvalidError):
            TelegramId("not-a-number")
    
    def test_empty_telegram_id(self):
        with pytest.raises(TelegramIdInvalidError):
            TelegramId("")

    def test_negative_telegram_id(self):
        with pytest.raises(TelegramIdInvalidError):
            TelegramId("-1234567890")

    def test_float_telegram_id(self):
        with pytest.raises(TelegramIdInvalidError):
            TelegramId("1234567890.1234567890")

    def test_zero_telegram_id(self):
        with pytest.raises(TelegramIdInvalidError):
            TelegramId("0")
    
    def test_long_telegram_id(self):
        with pytest.raises(TelegramIdInvalidError):
            TelegramId("123456789012345678901")