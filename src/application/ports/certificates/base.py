from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal


CertificateTheme = Literal["dark", "light"]


@dataclass(frozen=True, slots=True, kw_only=True)
class GiftCertificateData:
    brand: str
    title: str
    recipient_name: str
    gift_url: str
    unlock_password: str
    activates_at_label: str
    message: str | None = None
    theme: CertificateTheme = "dark"


class BaseGiftCertificateRenderer(ABC):
    @abstractmethod
    def render(self, data: GiftCertificateData) -> bytes: ...
