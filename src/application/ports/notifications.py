from abc import ABC, abstractmethod


class BaseEmailSender(ABC):
    @abstractmethod
    async def send_html(self, *, to: str, subject: str, html: str) -> None: ...


class BaseTelegramNotifier(ABC):
    @abstractmethod
    async def send_message(self, *, telegram_id: int, text: str) -> None: ...

    @abstractmethod
    async def send_photo(
        self,
        *,
        telegram_id: int,
        photo: bytes,
        filename: str,
        caption: str,
    ) -> None: ...
