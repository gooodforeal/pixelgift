from enum import StrEnum
from functools import lru_cache
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from datetime import datetime
import logging

from src.application.ports.notifications.base import (
    BaseEmailSender,
    BaseTelegramNotifier,
)
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
    unlock_password: str | None = None,
) -> str:
    password_block = ""
    if unlock_password:
        password_block = (
            '<tr><td align="center" style="padding: 20px 28px 0;">'
            '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
            'bgcolor="#140d29" style="border-radius: 16px; border: 1px solid #2a2348; '
            'background-color: #140d29;">'
            '<tr><td align="center" style="padding: 18px 20px;">'
            '<p style="margin: 0 0 8px; font-family: Manrope, Arial, sans-serif; '
            'font-size: 11px; font-weight: 600; letter-spacing: 0.14em; '
            'text-transform: uppercase; color: #64748b;">Пароль для открытия</p>'
            f'<p style="margin: 0; font-family: Unbounded, Manrope, Arial, sans-serif; '
            f'font-size: 22px; font-weight: 700; letter-spacing: 0.12em; color: #f5f3ff;">'
            f"{escape(unlock_password)}</p>"
            '<p style="margin: 10px 0 0; font-family: Manrope, Arial, sans-serif; '
            'font-size: 12px; line-height: 1.5; color: #94a3b8;">'
            "Введите его на странице подарка после окончания таймера</p>"
            "</td></tr></table></td></tr>"
        )

    return (
        _gift_ready_template()
        .replace("{{recipient_name}}", escape(recipient_name))
        .replace("{{title}}", escape(title))
        .replace("{{gift_url}}", escape(gift_url, quote=True))
        .replace("{{password_block}}", password_block)
    )


def _telegram_open_link(url: str) -> str:
    safe_url = escape(url, quote=True)
    return f'<a href="{safe_url}">{escape(url)}</a>'


def render_owner_telegram_html(
    event: OwnerTelegramEvent,
    *,
    box: Box,
    public_web_url: str,
) -> str:
    title = escape(box.title.value)
    name = escape(box.recipient_name.value)
    url = _gift_url(public_web_url, box.public_slug.value)
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
            "🎁 <b>Pixelgift</b>\n"
            "<b>Бокс опубликован</b>\n\n"
            f"<b>{title}</b>\n"
            f"для {name}\n\n"
            f"Откроется {activates}\n"
            f"{extra}\n\n"
            f"{_telegram_open_link(url)}"
        )

    if event is OwnerTelegramEvent.GIFT_READY:
        destination = f"на {email}" if email else "получателю"
        return (
            "🎁 <b>Pixelgift</b>\n"
            "<b>Письмо отправлено</b>\n\n"
            f"<b>{title}</b>\n"
            f"для {name} · {destination}\n\n"
            "Подарок уже можно открыть.\n\n"
            f"{_telegram_open_link(url)}"
        )

    if event is OwnerTelegramEvent.OPENED:
        if box.first_opened_at is None:
            raise ValueError("Box has not been opened yet")
        opened = escape(_format_local(box.first_opened_at, box.timezone))
        return (
            "🎁 <b>Pixelgift</b>\n"
            "<b>Подарок открыт</b>\n\n"
            f"{name} открыл(а) «{title}»\n"
            f"{opened}\n\n"
            f"{_telegram_open_link(url)}"
        )

    if event is OwnerTelegramEvent.ARCHIVED:
        return (
            "🎁 <b>Pixelgift</b>\n"
            "<b>Бокс в архиве</b>\n\n"
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
        "🎁 <b>Pixelgift</b>\n"
        "<b>Бокс восстановлен</b>\n\n"
        f"<b>{title}</b>\n"
        f"для {name}\n\n"
        f"Статус: {restored}.\n\n"
        f"{_telegram_open_link(url)}"
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
            unlock_password=(
                box.unlock_password.value if box.unlock_password is not None else None
            ),
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
