"""Задачи Taskiq: cron диспетчер уведомлений и ручной kick."""

from app.application.use_cases.boxes import ActivateDueBoxesUseCase
from app.application.use_cases.notifications import DispatchDueNotificationsUseCase
from app.infrastructure.worker.app import broker
from app.infrastructure.worker.deps import (
    get_activate_due_boxes_uc_dep,
    get_dispatch_due_notifications_uc_dep,
)
from taskiq_dependencies import Depends


@broker.task(schedule=[{"cron": "* * * * *"}])
async def dispatch_due_notifications(
    activate_uc: ActivateDueBoxesUseCase = Depends(get_activate_due_boxes_uc_dep),
    uc: DispatchDueNotificationsUseCase = Depends(
        get_dispatch_due_notifications_uc_dep
    ),
) -> int:
    """Каждую минуту активирует due-коробки и отправляет due-уведомления."""
    await activate_uc.execute()
    return await uc.execute()


@broker.task
async def kick_notification_dispatch(
    uc: DispatchDueNotificationsUseCase = Depends(
        get_dispatch_due_notifications_uc_dep
    ),
) -> int:
    """Немедленный запуск диспетчера после постановки jobs владельца."""
    return await uc.execute()
