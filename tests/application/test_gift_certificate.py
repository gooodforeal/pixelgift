from src.application.ports.certificates.base import GiftCertificateData
from src.infrastructure.certificates.gift_certificate_pdf import (
    ReportLabGiftCertificateRenderer,
)


def test_gift_certificate_pdf_dark_and_light():
    renderer = ReportLabGiftCertificateRenderer()
    for theme in ("dark", "light"):
        pdf = renderer.render(
            GiftCertificateData(
                brand="Pixelgift",
                title="День рождения",
                recipient_name="Маша",
                gift_url="http://localhost:8080/b/abc123",
                unlock_password="gift2026",
                activates_at_label="20.09.2026 18:00 (Europe/Moscow)",
                message="С любовью",
                theme=theme,  # type: ignore[arg-type]
            )
        )
        assert pdf.startswith(b"%PDF")
        assert len(pdf) > 2000
