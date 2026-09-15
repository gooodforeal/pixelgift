from uuid import UUID

from taskiq_dependencies import Depends

from src.application.use_cases.boxes import ActivateDueBoxesUseCase
from src.application.use_cases.notifications import (
    DispatchDueNotificationsUseCase,
    NotifyOwnerTelegramUseCase,
)
from src.infrastructure.worker.app import broker
from src.infrastructure.worker.deps import (
    get_activate_due_boxes_uc_dep,
    get_dispatch_due_notifications_uc_dep,
    get_notify_owner_telegram_uc_dep,
)


@broker.task(schedule=[{"cron": "* * * * *"}])
async def dispatch_due_notifications(
    activate_uc: ActivateDueBoxesUseCase = Depends(get_activate_due_boxes_uc_dep),
    uc: DispatchDueNotificationsUseCase = Depends(
        get_dispatch_due_notifications_uc_dep
    ),
) -> int:
    await activate_uc.execute()
    return await uc.execute()


@broker.task
async def notify_owner_telegram(
    box_id: str,
    event: str,
    uc: NotifyOwnerTelegramUseCase = Depends(get_notify_owner_telegram_uc_dep),
) -> bool:
    return await uc.execute(box_id=UUID(box_id), event=event)
