from taskiq_dependencies import DependencyGraph

from src.infrastructure.worker.tasks import (
    dispatch_due_notifications,
    kick_notification_dispatch,
)


def test_dispatch_due_notifications_uses_dependency_graph() -> None:
    graph = DependencyGraph(dispatch_due_notifications.original_func)
    assert not graph.is_empty()


def test_kick_notification_dispatch_uses_dependency_graph() -> None:
    graph = DependencyGraph(kick_notification_dispatch.original_func)
    assert not graph.is_empty()
