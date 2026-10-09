"""Порт рендеринга PDF подарочного сертификата."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal


CertificateTheme = Literal["dark", "light"]


@dataclass(frozen=True, slots=True, kw_only=True)
class GiftCertificateData:
    """Данные для отрисовки сертификата на одной странице PDF."""

    brand: str
    title: str
    recipient_name: str
    gift_url: str
    unlock_password: str
    activates_at_label: str
    message: str | None = None
    theme: CertificateTheme = "dark"


class BaseGiftCertificateRenderer(ABC):
    """Контракт адаптера генерации PDF (ReportLab, WeasyPrint и т.д.)."""

    @abstractmethod
    def render(self, data: GiftCertificateData) -> bytes:
        """Формирует бинарное содержимое PDF по переданным полям подарка."""
