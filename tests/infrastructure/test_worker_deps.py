from taskiq_dependencies import DependencyGraph

from src.infrastructure.worker.tasks import (
    dispatch_due_notifications,
    notify_owner_telegram,
)


def test_dispatch_due_notifications_uses_dependency_graph() -> None:
    graph = DependencyGraph(dispatch_due_notifications.original_func)
    assert not graph.is_empty()


def test_notify_owner_telegram_uses_dependency_graph() -> None:
    graph = DependencyGraph(notify_owner_telegram.original_func)
    assert not graph.is_empty()
