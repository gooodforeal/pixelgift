from taskiq_dependencies import Depends

from src.application.services.notifications import NotificationService
from src.application.use_cases.boxes import ActivateDueBoxesUseCase
from src.application.use_cases.notifications import DispatchDueNotificationsUseCase
from src.infrastructure.notifications.smtp_email import SmtpEmailSender
from src.infrastructure.notifications.telegram import TelegramBotNotifier
from src.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from src.settings import settings


def get_uow_dep() -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork()


def get_activate_due_boxes_uc_dep(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow_dep),
) -> ActivateDueBoxesUseCase:
    return ActivateDueBoxesUseCase(uow)


def get_notification_service_dep() -> NotificationService:
    return NotificationService(
        SmtpEmailSender(settings),
        TelegramBotNotifier(settings),
        public_web_url=settings.public_web_url,
    )


def get_dispatch_due_notifications_uc_dep(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow_dep),
    notifications: NotificationService = Depends(get_notification_service_dep),
) -> DispatchDueNotificationsUseCase:
    return DispatchDueNotificationsUseCase(
        uow,
        notifications,
        max_attempts=settings.notification_max_attempts,
        processing_stale_minutes=settings.notification_processing_stale_minutes,
    )
