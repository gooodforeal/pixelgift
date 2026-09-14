from functools import lru_cache
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from datetime import datetime

from src.application.ports.notifications import BaseEmailSender, BaseTelegramNotifier
from src.domain.aggregates.boxes import Box
from src.domain.entities.users import User

_SRC_ROOT = Path(__file__).resolve().parents[2]
_GIFT_READY_TEMPLATE = _SRC_ROOT / "static" / "email" / "gift_ready.html"


def _format_opened_at(value: datetime, timezone_name: str) -> str:
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        tz = ZoneInfo("UTC")
    local = value.astimezone(tz)
    return local.strftime("%d.%m.%Y в %H:%M")


def _gift_url(public_web_url: str, slug: str) -> str:
    return f"{public_web_url.rstrip('/')}/b/{slug}"


@lru_cache(maxsize=1)
def _gift_ready_template() -> str:
    return _GIFT_READY_TEMPLATE.read_text(encoding="utf-8")


def render_gift_ready_html(
    *,
    recipient_name: str,
    title: str,
    gift_url: str,
) -> str:
    return (
        _gift_ready_template()
        .replace("{{recipient_name}}", escape(recipient_name))
        .replace("{{title}}", escape(title))
        .replace("{{gift_url}}", escape(gift_url, quote=True))
    )


class NotificationService:
    """Отправляет письмо получателю и Telegram-уведомления отправителю."""

    def __init__(
        self,
        email_sender: BaseEmailSender,
        telegram_notifier: BaseTelegramNotifier,
        *,
        public_web_url: str,
    ) -> None:
        self._email = email_sender
        self._telegram = telegram_notifier
        self._public_web_url = public_web_url

    async def notify_gift_ready(self, *, box: Box, owner: User) -> None:
        if box.recipient_email is None:
            raise ValueError("Box has no recipient email")

        gift_url = _gift_url(self._public_web_url, box.public_slug.value)
        html = render_gift_ready_html(
            recipient_name=box.recipient_name.value,
            title=box.title.value,
            gift_url=gift_url,
        )
        subject = f"🎁 {box.recipient_name.value}, тебе подарок: {box.title.value}"
        await self._email.send_html(
            to=box.recipient_email.value,
            subject=subject,
            html=html,
        )
        await self._telegram.send_message(
            telegram_id=int(owner.telegram_id.value),
            text=(
                f"🎁 Подарок «{box.title.value}» отправлен "
                f"{box.recipient_name.value} на {box.recipient_email.value}"
            ),
        )

    async def notify_box_opened(self, *, box: Box, owner: User) -> None:
        if box.first_opened_at is None:
            raise ValueError("Box has not been opened yet")

        opened_label = _format_opened_at(box.first_opened_at, box.timezone)
        await self._telegram.send_message(
            telegram_id=int(owner.telegram_id.value),
            text=(
                f"✨ {box.recipient_name.value} открыл(а) подарок "
                f"«{box.title.value}» {opened_label}"
            ),
        )
