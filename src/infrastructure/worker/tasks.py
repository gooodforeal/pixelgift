from uuid import UUID

from src.application.services.notifications import NotificationService
from src.application.use_cases.notifications import (
    DispatchDueNotificationsUseCase,
    NotifyBoxOpenedUseCase,
)
from src.infrastructure.notifications.smtp_email import SmtpEmailSender
from src.infrastructure.notifications.telegram import TelegramBotNotifier
from src.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from src.infrastructure.worker.app import broker
from src.settings import settings


def _notifications() -> NotificationService:
    return NotificationService(
        SmtpEmailSender(settings),
        TelegramBotNotifier(settings),
        public_web_url=settings.public_web_url,
    )


@broker.task(schedule=[{"cron": "* * * * *"}])
async def dispatch_due_notifications() -> int:
    return await DispatchDueNotificationsUseCase(
        SqlAlchemyUnitOfWork(),
        _notifications(),
    ).execute()


@broker.task
async def notify_box_opened(box_id: str) -> bool:
    return await NotifyBoxOpenedUseCase(
        SqlAlchemyUnitOfWork(),
        _notifications(),
    ).execute(box_id=UUID(box_id))
