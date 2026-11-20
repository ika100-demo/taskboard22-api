# Verification — 001 Create and list tasks (in memory)

**Result:** pass
**Commit:** 79afffb · **Base:** 064de48 · **Trace:** 7/7 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-001.1 | met | `tests/test_tasks.py::test_ac_001_1_create_task_with_title_only`, `tests/test_smoke_tasks.py::test_ac_001_1_smoke_create_task` | `src/taskboard22_api/tasks/router.py:19`, `src/taskboard22_api/tasks/store.py:18`, `src/taskboard22_api/main.py:27` | asserts 201, non-empty string `id`, `title == "Buy milk"`, `due_date is None` |
| AC-001.2 | met | `tests/test_tasks.py::test_ac_001_2_create_task_with_due_date` | `src/taskboard22_api/tasks/models.py:27`, `src/taskboard22_api/tasks/router.py:19` | asserts 201, `due_date == "2026-12-31"`, title and non-empty id |
| AC-001.3 | met | `tests/test_tasks.py::test_ac_001_3_invalid_title_is_rejected` (missing, null, empty, whitespace, tabs/newlines, 201 chars), `::test_ac_001_3_title_of_200_characters_is_accepted` | `src/taskboard22_api/tasks/models.py:17`, `src/taskboard22_api/tasks/models.py:20` | asserts 422, `["body","title"]` in `detail[].loc`, and `GET /tasks == []` afterwards; 200-char boundary accepted |
| AC-001.4 | met | `tests/test_tasks.py::test_ac_001_4_invalid_due_date_is_rejected` (`2026-02-30`, `31.12.2026`, `tomorrow`) | `src/taskboard22_api/tasks/models.py:27-38` | asserts 422, `["body","due_date"]` in `loc`, and empty list afterwards |
| AC-001.5 | met | `tests/test_tasks.py::test_ac_001_5_list_returns_created_tasks_oldest_first`, `tests/test_smoke_tasks.py::test_ac_001_5_smoke_list_contains_created_task` | `src/taskboard22_api/tasks/router.py:27`, `src/taskboard22_api/tasks/store.py:24` | asserts 200 and list equals the three creation bodies in order (each once, fields exact) |
| AC-001.6 | met | `tests/test_tasks.py::test_ac_001_6_list_is_empty_initially` | `src/taskboard22_api/tasks/store.py:14`, `src/taskboard22_api/tasks/router.py:27` | asserts 200 and `[]` with a fresh store |
| AC-001.7 | met | `tests/test_tasks.py::test_ac_001_7_duplicate_titles_get_different_ids` | `src/taskboard22_api/tasks/store.py:19` (uuid4 id, no uniqueness check on title) | asserts both 201, distinct ids, list equals both bodies |

## Non-goals

No durable storage, single-task read, update/complete/delete, filtering/sorting/pagination, auth, or due times were added. No template-owned layout changes (`main.py` only gains `include_router`). ✔

## Deviations from the plan

none. Every changed source file is in t1's `files`; t1 is `done: true`. Test files and spec docs are outside task `files` as expected (acceptance tests and spec lifecycle); acceptable.

## Contract

Matches `design.md`: 201 body `{id, title, due_date}`, FastAPI default 422 with `loc ["body", "<field>"]`, `GET /tasks` array oldest first, `extra="ignore"` default kept, `task_created` log carries only `task_id`. No `contract/` copy exists, so no contract cases apply. ✔

## Observations (not criteria)

- Both task smoke tests are `@pytest.mark.writes`, so staging and prod have no read-only smoke check for `/tasks` (CLAUDE.md asks for one per behaviour checked there); a read-only `GET /tasks` returns-200-array smoke test would cover it.

## Mutation check (report only)

10 of 14 mutants of the changed code were caught by the acceptance tests (71 %; spec 152, report only).

Survived (a test that names the criterion would fail if it checked this):
- `src/taskboard22_api/tasks/models.py:31 return value → None`
- `src/taskboard22_api/tasks/models.py:17 1 → 2`
- `src/taskboard22_api/tasks/models.py:17 200 → 201`
- `src/taskboard22_api/tasks/store.py:34 return value → None`
