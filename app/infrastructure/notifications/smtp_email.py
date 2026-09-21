from email.message import EmailMessage

import aiosmtplib

from app.application.ports.notifications.base import BaseEmailSender
from app.settings import Settings


class SmtpEmailSender(BaseEmailSender):
    def __init__(self, settings: Settings) -> None:
        self._host = settings.smtp_host
        self._port = settings.smtp_port
        self._username = settings.smtp_username
        self._password = settings.smtp_password
        self._from_email = settings.smtp_from_email
        self._use_tls = settings.smtp_use_tls

    async def send_html(self, *, to: str, subject: str, html: str) -> None:
        message = EmailMessage()
        message["From"] = self._from_email
        message["To"] = to
        message["Subject"] = subject
        message.set_content(
            "Открой подарок по ссылке в HTML-версии этого письма.",
            subtype="plain",
        )
        message.add_alternative(html, subtype="html")

        # Gmail: 465 = implicit TLS, 587 = STARTTLS; Mailpit = neither
        use_tls = self._use_tls and self._port == 465
        start_tls = self._use_tls and self._port != 465

        await aiosmtplib.send(
            message,
            hostname=self._host,
            port=self._port,
            username=self._username or None,
            password=self._password or None,
            use_tls=use_tls,
            start_tls=start_tls,
            timeout=30,
        )
