"""HTTP routes for tasks."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends

from .models import Task, TaskCreate
from .store import TaskStore, get_task_store

router = APIRouter(tags=["tasks"])
log = structlog.get_logger(__name__)

StoreDep = Annotated[TaskStore, Depends(get_task_store)]


@router.post("/tasks", status_code=201, response_model=Task)
def create_task(body: TaskCreate, store: StoreDep) -> Task:
    """Create a task."""
    task = store.add(body.title, body.due_date)
    log.info("task_created", task_id=task.id)
    return task


@router.get("/tasks", response_model=list[Task])
def list_tasks(store: StoreDep) -> list[Task]:
    """List all tasks, oldest first."""
    return store.list()
