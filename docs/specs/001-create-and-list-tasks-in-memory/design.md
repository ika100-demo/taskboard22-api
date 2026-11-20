# Design — 001 Create and list tasks (in memory)

## Decisions

- Tasks live in a process-local `TaskStore` (a list guarded by a `threading.Lock`), because the spec rules out durable storage and accepts per-instance state (non-goals). Sync FastAPI handlers run in a thread pool, so appends and snapshots take the lock. No ADR: the store is a stand-in a later storage spec replaces behind the same interface.
- The store reaches handlers through a FastAPI dependency `get_task_store()` returning a module-level singleton, so tests get a fresh, empty store per test with `app.dependency_overrides[get_task_store] = lambda: TaskStore()` (needed for AC-001.6 and the "no new task" checks of AC-001.3/AC-001.4).
- Validation errors use FastAPI's default `422` body (`{"detail": [{"loc": [...], "msg": ..., "type": ...}]}`) instead of a custom error format: it already names the field in `loc` (AC-001.3, AC-001.4) and is what the framework the service is built on returns for every other request; a project-wide problem+json format would be its own spec.
- `due_date` is validated as a string matching `^\d{4}-\d{2}-\d{2}$` and parsed with `datetime.date.fromisoformat`, not as a pydantic `date`: pydantic's lax `date` also accepts Unix timestamps and zero-time datetime strings, which AC-001.4 must reject. The value is stored and returned as the string sent (identical to its ISO form, given the pattern).
- `title` is a `StrictStr` (no int-to-str coercion), `min_length=1`, `max_length=200` (counted in Unicode code points), plus a validator rejecting whitespace-only values; it is never stripped, so it is returned exactly as sent (A3).
- Unknown request fields are ignored (pydantic default `extra="ignore"`) (A7).
- `id` is `str(uuid.uuid4())` (A2).

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/taskboard22_api/tasks/__init__.py` | exports `router`, `TaskStore`, `get_task_store` | new |
| `src/taskboard22_api/tasks/models.py` | `TaskCreate` (request), `Task` (response) pydantic models and validators | new |
| `src/taskboard22_api/tasks/store.py` | `TaskStore`, `get_task_store()` | new |
| `src/taskboard22_api/tasks/router.py` | `APIRouter` with `POST /tasks`, `GET /tasks` | new |
| `src/taskboard22_api/main.py` | `app.include_router(tasks.router)` | changed |

Interfaces:

```python
class TaskCreate(BaseModel):          # extra fields ignored
    title: StrictStr                  # 1..200 chars, not whitespace-only, unchanged
    due_date: StrictStr | None = None # YYYY-MM-DD, real calendar date

class Task(BaseModel):
    id: str
    title: str
    due_date: str | None

class TaskStore:
    def add(self, title: str, due_date: str | None) -> Task: ...  # new uuid4 id, appends
    def list(self) -> list[Task]: ...                              # copy, creation order

def get_task_store() -> TaskStore: ...  # module-level singleton
```

## Contract

All bodies are `application/json`.

`POST /tasks`

- Request: `{"title": string, "due_date": string | null (optional)}`. Other fields are ignored.
  - `title`: required, a JSON string, 1 to 200 characters, not only whitespace; returned exactly as sent; duplicates allowed (AC-001.3, AC-001.7).
  - `due_date`: optional, absent or `null` means no due date; otherwise a JSON string `YYYY-MM-DD` that is a real calendar date; past dates are accepted (AC-001.2, AC-001.4).
- `201` → `{"id": string (UUID v4, non-empty, unique), "title": string, "due_date": string "YYYY-MM-DD" | null}` (AC-001.1, AC-001.2, AC-001.7).
- `422` → `{"detail": [{"loc": ["body", "<field>"], "msg": string, "type": string, ...}, ...]}` where `<field>` is `title` or `due_date`. One entry per offending field. Missing `title`, `null`, empty, whitespace-only, over 200 characters or a non-string all give an entry with `loc == ["body", "title"]`; an invalid `due_date` gives `loc == ["body", "due_date"]`. A body that is not a JSON object also answers `422` (`loc == ["body"]`). No task is stored on `422` (AC-001.3, AC-001.4).

`GET /tasks`

- `200` → JSON array of `Task` objects as returned on creation, oldest first, every task once; `[]` when none exist since start (AC-001.5, AC-001.6). No query parameters, no pagination.

Tasks are per process and lost on restart.

## Data

In memory only: `list[Task]` in `TaskStore`, insertion order = creation order. No migration.
