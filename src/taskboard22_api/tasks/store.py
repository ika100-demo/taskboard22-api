"""In-memory task store."""

from __future__ import annotations

import threading
import uuid

from .models import Task


class TaskStore:
    """Process-local task storage, safe for use from thread-pool handlers."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tasks: list[Task] = []

    def add(self, title: str, due_date: str | None) -> Task:
        task = Task(id=str(uuid.uuid4()), title=title, due_date=due_date)
        with self._lock:
            self._tasks.append(task)
        return task

    def list(self) -> list[Task]:
        with self._lock:
            return list(self._tasks)


_store = TaskStore()


def get_task_store() -> TaskStore:
    """FastAPI dependency returning the process-wide store."""
    return _store
