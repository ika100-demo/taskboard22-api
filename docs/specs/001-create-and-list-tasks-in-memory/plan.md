---
spec_id: 001-create-and-list-tasks-in-memory
shape: service-python
spec_hash: 262c6d73eed4
summary: In-memory POST /tasks and GET /tasks with title and optional due date
tasks:
  - id: t1
    title: Add in-memory tasks module with POST /tasks and GET /tasks
    files: [src/taskboard22_api/tasks/__init__.py, src/taskboard22_api/tasks/models.py, src/taskboard22_api/tasks/store.py, src/taskboard22_api/tasks/router.py, src/taskboard22_api/main.py]
    covers: [AC-001.1, AC-001.2, AC-001.3, AC-001.4, AC-001.5, AC-001.6, AC-001.7]
    parallel_safe: true
    depends_on: []
---

# Plan — 001 Create and list tasks (in memory)

One task: the models, store and router are each only checkable through the endpoints, so splitting them would leave a task whose acceptance tests cannot pass alone. Contract and module layout: [design.md](design.md).

## t1 — Add in-memory tasks module with POST /tasks and GET /tasks

**Files:** src/taskboard22_api/tasks/__init__.py, src/taskboard22_api/tasks/models.py, src/taskboard22_api/tasks/store.py, src/taskboard22_api/tasks/router.py, src/taskboard22_api/main.py
**Covers:** AC-001.1, AC-001.2, AC-001.3, AC-001.4, AC-001.5, AC-001.6, AC-001.7
**Goal:** Clients can create a task with a title and optional due date and list all tasks in creation order, held in process memory, with the exact contract in design.md.

**Implementation notes:**
- `models.py`: `TaskCreate` with `title: Annotated[StrictStr, StringConstraints(min_length=1, max_length=200)]` plus a `field_validator` rejecting whitespace-only (no stripping); `due_date: StrictStr | None = None` with a validator requiring `^\d{4}-\d{2}-\d{2}$` and `date.fromisoformat` succeeding. Raise `ValueError` so FastAPI's default 422 carries `loc ["body", "<field>"]`. Keep the default `extra="ignore"`.
- `models.py`: `Task` response model `id: str`, `title: str`, `due_date: str | None`.
- `store.py`: `TaskStore` with a `threading.Lock`, `add(title, due_date) -> Task` (id `str(uuid.uuid4())`, append) and `list() -> list[Task]` (copy under the lock); module-level `_store = TaskStore()` and `get_task_store() -> TaskStore`.
- `router.py`: `APIRouter(tags=["tasks"])`; `POST /tasks` `status_code=201`, `response_model=Task`, store injected with `Depends(get_task_store)`; `GET /tasks` `response_model=list[Task]`. Sync handlers.
- `__init__.py`: export `router`, `TaskStore`, `get_task_store`, `Task`, `TaskCreate`.
- `main.py`: `app.include_router(tasks.router)`; nothing else changes.
- Log one structlog event `task_created` with `task_id` (never the title) on create.
- Do not add a custom exception handler; the 422 body is FastAPI's default.

**Done when:** the acceptance tests for AC-001.1 to AC-001.7 pass (tests isolate state via `app.dependency_overrides[get_task_store]`), existing health/metrics tests still pass, and `devbox run ci` is green.
