from abc import ABC, abstractmethod


class BaseEmailSender(ABC):
    @abstractmethod
    async def send_html(self, *, to: str, subject: str, html: str) -> None: ...


class BaseTelegramNotifier(ABC):
    @abstractmethod
    async def send_message(self, *, telegram_id: int, text: str) -> None: ...
