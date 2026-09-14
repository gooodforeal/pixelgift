from email.message import EmailMessage
import asyncio
import smtplib

from src.application.ports.notifications import BaseEmailSender
from src.settings import Settings


class SmtpEmailSender(BaseEmailSender):
    def __init__(self, settings: Settings) -> None:
        self._host = settings.smtp_host
        self._port = settings.smtp_port
        self._username = settings.smtp_username
        self._password = settings.smtp_password
        self._from_email = settings.smtp_from_email
        self._use_tls = settings.smtp_use_tls

    async def send_html(self, *, to: str, subject: str, html: str) -> None:
        await asyncio.to_thread(self._send, to, subject, html)

    def _send(self, to: str, subject: str, html: str) -> None:
        message = EmailMessage()
        message["From"] = self._from_email
        message["To"] = to
        message["Subject"] = subject
        message.set_content(
            "Открой подарок по ссылке в HTML-версии этого письма.",
            subtype="plain",
        )
        message.add_alternative(html, subtype="html")

        with smtplib.SMTP(self._host, self._port, timeout=20) as smtp:
            if self._use_tls:
                smtp.starttls()
            if self._username:
                smtp.login(self._username, self._password)
            smtp.send_message(message)
