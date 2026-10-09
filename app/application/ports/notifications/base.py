"""Порты доставки email и Telegram."""

from abc import ABC, abstractmethod


class BaseEmailSender(ABC):
    """Контракт адаптера отправки HTML-писем (SMTP, SendGrid и т.п.)."""

    @abstractmethod
    async def send_html(self, *, to: str, subject: str, html: str) -> None:
        """Отправляет письмо с HTML-телом на указанный адрес."""


class BaseTelegramNotifier(ABC):
    """Контракт адаптера Bot API Telegram для уведомлений владельца."""

    @abstractmethod
    async def send_message(self, *, telegram_id: int, text: str) -> None:
        """Отправляет текстовое сообщение пользователю по telegram_id."""

    @abstractmethod
    async def send_photo(
        self,
        *,
        telegram_id: int,
        photo: bytes,
        filename: str,
        caption: str,
    ) -> None:
        """Отправляет изображение с подписью (HTML-разметка в caption, если поддерживается)."""
