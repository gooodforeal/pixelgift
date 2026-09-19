from email.message import EmailMessage
import asyncio
import smtplib
import ssl

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

        context = ssl.create_default_context()
        # Gmail: 465 = implicit SSL, 587 = STARTTLS
        if self._use_tls and self._port == 465:
            with smtplib.SMTP_SSL(
                self._host, self._port, timeout=30, context=context
            ) as smtp:
                self._authenticate_and_send(smtp, message)
            return

        with smtplib.SMTP(self._host, self._port, timeout=30) as smtp:
            if self._use_tls:
                smtp.starttls(context=context)
            self._authenticate_and_send(smtp, message)

    def _authenticate_and_send(
        self, smtp: smtplib.SMTP, message: EmailMessage
    ) -> None:
        if self._username:
            smtp.login(self._username, self._password)
        smtp.send_message(message)
