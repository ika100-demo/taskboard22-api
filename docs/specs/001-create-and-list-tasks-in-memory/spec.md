---
spec_id: 001-create-and-list-tasks-in-memory
title: Create and list tasks (in memory)
status: done
priority: P1
shape: service-python
---

# 001 — Create and list tasks (in memory)

## Problem

The Task API has no tasks yet: it only answers health and metrics, so a client has nothing to record work in. Clients need the smallest useful core, creating a task with a title and an optional due date and listing the tasks, to start building against the API. Keeping tasks in memory gets that core usable now, without deciding on storage first.

## Stories

As an API client, I want to create a task with a title and, if I have one, a due date, so that I can record work to be done.

As an API client, I want to list all tasks, so that I can show what has been recorded.

## Acceptance criteria

- **AC-001.1** Given the service is running, when a client sends `POST /tasks` with `{"title": "Buy milk"}`, then the response is `201` with a JSON body holding a non-empty string `id`, `"title": "Buy milk"` and `"due_date": null`. (smoke)
- **AC-001.2** Given the service is running, when a client sends `POST /tasks` with `{"title": "File taxes", "due_date": "2026-12-31"}`, then the response is `201` and the body holds `"due_date": "2026-12-31"` along with the `id` and `title`.
- **AC-001.3** Given the service is running, when a client sends `POST /tasks` with the `title` missing, `null`, empty, whitespace only, or longer than 200 characters, then the response is `422` with a body naming the field `title`, and `GET /tasks` afterwards lists no new task.
- **AC-001.4** Given the service is running, when a client sends `POST /tasks` with a `due_date` that is not a real calendar date in `YYYY-MM-DD` form (for example `"2026-02-30"`, `"31.12.2026"` or `"tomorrow"`), then the response is `422` with a body naming the field `due_date`, and `GET /tasks` afterwards lists no new task.
- **AC-001.5** Given tasks were created, when a client sends `GET /tasks`, then the response is `200` with a JSON array holding every created task once, each with `id`, `title` and `due_date` exactly as returned on creation, in the order they were created (oldest first). (smoke)
- **AC-001.6** Given the service started and no task was created since, when a client sends `GET /tasks`, then the response is `200` with an empty JSON array `[]`.
- **AC-001.7** Given a task titled "Buy milk" exists, when a client creates another task titled "Buy milk", then the response is `201` with an `id` different from the first task's, and `GET /tasks` lists both.

## Non-goals

- Durable storage: tasks are lost when the service restarts, and each running instance keeps its own tasks.
- Reading a single task, updating, completing or deleting tasks.
- Filtering, sorting options, search and pagination of the list.
- Authentication, users and per-user task lists.
- Due times and time zones; a due date is a calendar date only.

## Assumptions

- **A1** Endpoints are `POST /tasks` (create) and `GET /tasks` (list), with JSON fields `id`, `title`, `due_date` (other option: other paths or field names such as `dueDate`; affects AC-001.1, AC-001.2, AC-001.5).
- **A2** `id` is a server-generated opaque unique string, e.g. a UUID (other option: sequential integers; affects AC-001.1, AC-001.7).
- **A3** A title is required, 1 to 200 characters, not whitespace only, and is returned exactly as sent; duplicates are allowed (other option: trim whitespace, other length limit, unique titles; affects AC-001.3, AC-001.7).
- **A4** A due date is an ISO 8601 calendar date `YYYY-MM-DD`, optional, `null` when absent; past dates are accepted (other option: date-time with time zone, reject past dates; affects AC-001.2, AC-001.4).
- **A5** Invalid input answers `422` with a body naming the offending field (other option: `400`; affects AC-001.3, AC-001.4).
- **A6** The list returns all tasks in creation order, oldest first, without a size limit or cap on the number of tasks kept (other option: newest first, a cap; affects AC-001.5).
- **A7** Fields a client sends beyond `title` and `due_date` are ignored (other option: reject with `422`; affects AC-001.1, AC-001.2).

## Open questions

none

<!-- Priority levels (spec 196) for the product-manager's PRIORITY line: P0 an outage, data loss, a security problem, or something that blocks all other work; P1 a normal bug or feature; the fallback when nothing signals urgency; P2 cosmetic, a convenience, or something with an easy workaround. A reason is "P<n>: <phrase>", one of: P0: outage, data loss, security problem, blocks all other work; P1: normal bug or feature; P2: cosmetic, convenience, easy workaround. -->

## Changelog

- 2026-11-20 created
- 2026-11-20 priority P1 proposed: P1: normal bug or feature
- 2026-11-20 approved
- 2026-11-20 building
- 2026-11-20 done
