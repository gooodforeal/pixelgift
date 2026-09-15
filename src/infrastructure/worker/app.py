from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import ListQueueBroker

from src.settings import settings

broker = ListQueueBroker(
    url=settings.redis_url,
    socket_timeout=None,
    socket_connect_timeout=5,
)
scheduler = TaskiqScheduler(broker, sources=[LabelScheduleSource(broker)])

from src.infrastructure.worker.tasks import (  # noqa: E402, F401
    dispatch_due_notifications,
    notify_owner_telegram,
)
