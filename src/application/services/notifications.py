from enum import StrEnum
from functools import lru_cache
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from datetime import datetime
import logging

from src.application.ports.notifications import BaseEmailSender, BaseTelegramNotifier
from src.domain.aggregates.boxes import Box, BoxStatus
from src.domain.entities.users import User

logger = logging.getLogger(__name__)

_SRC_ROOT = Path(__file__).resolve().parents[2]
_GIFT_READY_TEMPLATE = _SRC_ROOT / "static" / "email" / "gift_ready.html"
_TELEGRAM_CARDS = _SRC_ROOT / "static" / "telegram"


class OwnerTelegramEvent(StrEnum):
    PUBLISHED = "published"
    GIFT_READY = "gift_ready"
    OPENED = "opened"
    ARCHIVED = "archived"
    UNARCHIVED = "unarchived"


_CARD_FILES = {
    OwnerTelegramEvent.PUBLISHED: "tg-published.png",
    OwnerTelegramEvent.GIFT_READY: "tg-sent.png",
    OwnerTelegramEvent.OPENED: "tg-opened.png",
    OwnerTelegramEvent.ARCHIVED: "tg-archived.png",
    OwnerTelegramEvent.UNARCHIVED: "tg-restored.png",
}


def _format_local(value: datetime, timezone_name: str) -> str:
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


@lru_cache(maxsize=8)
def _telegram_card(filename: str) -> bytes | None:
    path = _TELEGRAM_CARDS / filename
    if not path.is_file():
        return None
    return path.read_bytes()


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


def render_owner_telegram_html(
    event: OwnerTelegramEvent,
    *,
    box: Box,
    public_web_url: str,
) -> str:
    title = escape(box.title.value)
    name = escape(box.recipient_name.value)
    url = _gift_url(public_web_url, box.public_slug.value)
    safe_url = escape(url, quote=True)
    activates = escape(_format_local(box.activates_at.value, box.timezone))
    email = (
        escape(box.recipient_email.value) if box.recipient_email is not None else None
    )

    if event is OwnerTelegramEvent.PUBLISHED:
        extra = (
            f"Письмо уйдёт на {email} в этот момент."
            if email
            else "Письмо не запланировано — у бокса нет почты получателя."
        )
        return (
            "<b>Pixelgift</b>\n"
            "Бокс опубликован\n\n"
            f"<b>{title}</b>\n"
            f"для {name}\n\n"
            f"Откроется {activates}\n"
            f"{extra}\n\n"
            f'<a href="{safe_url}">Открыть ссылку</a>'
        )

    if event is OwnerTelegramEvent.GIFT_READY:
        destination = f"на {email}" if email else "получателю"
        return (
            "<b>Pixelgift</b>\n"
            "Письмо отправлено\n\n"
            f"<b>{title}</b>\n"
            f"для {name} · {destination}\n\n"
            "Подарок уже можно открыть.\n"
            f'<a href="{safe_url}">Открыть ссылку</a>'
        )

    if event is OwnerTelegramEvent.OPENED:
        if box.first_opened_at is None:
            raise ValueError("Box has not been opened yet")
        opened = escape(_format_local(box.first_opened_at, box.timezone))
        return (
            "<b>Pixelgift</b>\n"
            "Подарок открыт\n\n"
            f"{name} открыл(а) «{title}»\n"
            f"{opened}"
        )

    if event is OwnerTelegramEvent.ARCHIVED:
        return (
            "<b>Pixelgift</b>\n"
            "Бокс в архиве\n\n"
            f"<b>{title}</b>\n"
            f"для {name}\n\n"
            "Ссылка больше не откроет подарок."
        )

    restored = (
        "снова ожидает открытия"
        if box.status in {BoxStatus.SCHEDULED, BoxStatus.ACTIVE}
        else "снова черновик"
    )
    return (
        "<b>Pixelgift</b>\n"
        "Бокс восстановлен\n\n"
        f"<b>{title}</b>\n"
        f"для {name}\n\n"
        f"Статус: {restored}."
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
        await self.notify_owner_telegram(
            box=box, owner=owner, event=OwnerTelegramEvent.GIFT_READY
        )

    async def notify_owner_telegram(
        self,
        *,
        box: Box,
        owner: User,
        event: OwnerTelegramEvent,
    ) -> None:
        caption = render_owner_telegram_html(
            event, box=box, public_web_url=self._public_web_url
        )
        telegram_id = int(owner.telegram_id.value)
        filename = _CARD_FILES[event]
        photo = _telegram_card(filename)
        if photo is None:
            logger.warning("Telegram card missing: %s", filename)
            await self._telegram.send_message(telegram_id=telegram_id, text=caption)
            return
        await self._telegram.send_photo(
            telegram_id=telegram_id,
            photo=photo,
            filename=filename,
            caption=caption,
        )
