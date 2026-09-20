from dataclasses import dataclass
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from datetime import datetime
import uuid

from src.application.ports.certificates.base import (
    BaseGiftCertificateRenderer,
    CertificateTheme,
    GiftCertificateData,
)
from src.application.uow.base import BaseUnitOfWork
from src.domain.aggregates.boxes import BoxStatus
from src.domain.exceptions.boxes import (
    BoxAccessDeniedError,
    BoxCertificateNotAvailableError,
    BoxNotFoundError,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class GiftCertificateFile:
    data: bytes
    filename: str
    media_type: str = "application/pdf"


def _format_local(value: datetime, timezone_name: str) -> str:
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        tz = ZoneInfo("UTC")
        timezone_name = "UTC"
    local = value.astimezone(tz)
    return f"{local.strftime('%d.%m.%Y %H:%M')} ({timezone_name})"


def _gift_url(public_web_url: str, slug: str) -> str:
    return f"{public_web_url.rstrip('/')}/b/{slug}"


class GenerateGiftCertificateUseCase:
    def __init__(
        self,
        uow: BaseUnitOfWork,
        renderer: BaseGiftCertificateRenderer,
        *,
        public_web_url: str,
    ) -> None:
        self._uow = uow
        self._renderer = renderer
        self._public_web_url = public_web_url

    async def execute(
        self,
        *,
        box_id: uuid.UUID,
        actor_id: uuid.UUID,
        theme: CertificateTheme = "dark",
    ) -> GiftCertificateFile:
        async with self._uow as uow:
            box = await uow.boxes.get_by_id(box_id)
            if box is None:
                raise BoxNotFoundError(box_id)
            if box.owner_id != actor_id:
                raise BoxAccessDeniedError(box_id, actor_id)
            if box.status == BoxStatus.DRAFT:
                raise BoxCertificateNotAvailableError(box_id, box.status.value)

            password = (
                box.unlock_password.value if box.unlock_password is not None else ""
            )
            message = box.message.value if box.message is not None else None
            data = GiftCertificateData(
                brand="Pixelgift",
                title=box.title.value,
                recipient_name=box.recipient_name.value,
                gift_url=_gift_url(self._public_web_url, box.public_slug.value),
                unlock_password=password or "—",
                activates_at_label=_format_local(box.activates_at.value, box.timezone),
                message=message,
                theme=theme,
            )
            pdf = self._renderer.render(data)
            safe_slug = box.public_slug.value.replace("/", "-")
            return GiftCertificateFile(
                data=pdf,
                filename=f"pixelgift-{safe_slug}-{theme}.pdf",
            )
