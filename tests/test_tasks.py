"""Acceptance tests for spec 001: create and list tasks (in memory)."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from taskboard22_api.main import app


@pytest.fixture()
def tasks_client() -> Iterator[TestClient]:
    """A client whose task store is fresh and private to the test."""
    try:
        from taskboard22_api.tasks import TaskStore, get_task_store
    except ImportError as err:  # behaviour not built yet
        pytest.fail(f"spec 001 not implemented: taskboard22_api.tasks missing ({err})")
    store = TaskStore()
    app.dependency_overrides[get_task_store] = lambda: store
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_task_store, None)


def _field_names(body: dict[str, Any]) -> list[Any]:
    return [entry["loc"][-1] for entry in body["detail"] if entry["loc"][0] == "body"]


def test_ac_001_1_create_task_with_title_only(tasks_client: TestClient) -> None:  # AC-001.1
    response = tasks_client.post("/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    body = response.json()
    assert isinstance(body["id"], str)
    assert body["id"] != ""
    assert body["title"] == "Buy milk"
    assert body["due_date"] is None


def test_ac_001_2_create_task_with_due_date(tasks_client: TestClient) -> None:  # AC-001.2
    response = tasks_client.post("/tasks", json={"title": "File taxes", "due_date": "2026-12-31"})
    assert response.status_code == 201
    body = response.json()
    assert body["due_date"] == "2026-12-31"
    assert body["title"] == "File taxes"
    assert isinstance(body["id"], str)
    assert body["id"] != ""


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": None},
        {"title": ""},
        {"title": "   "},
        {"title": "\t\n "},
        {"title": "x" * 201},
    ],
    ids=["missing", "null", "empty", "whitespace", "whitespace-tabs-newlines", "too-long"],
)
def test_ac_001_3_invalid_title_is_rejected(  # AC-001.3
    tasks_client: TestClient, payload: dict[str, Any]
) -> None:
    response = tasks_client.post("/tasks", json=payload)
    assert response.status_code == 422
    assert ["body", "title"] in [entry["loc"] for entry in response.json()["detail"]]
    listed = tasks_client.get("/tasks")
    assert listed.status_code == 200
    assert listed.json() == []


def test_ac_001_3_title_of_200_characters_is_accepted(  # AC-001.3
    tasks_client: TestClient,
) -> None:
    response = tasks_client.post("/tasks", json={"title": "x" * 200})
    assert response.status_code == 201
    assert response.json()["title"] == "x" * 200


@pytest.mark.parametrize(
    "due_date",
    ["2026-02-30", "31.12.2026", "tomorrow"],
)
def test_ac_001_4_invalid_due_date_is_rejected(  # AC-001.4
    tasks_client: TestClient, due_date: str
) -> None:
    response = tasks_client.post("/tasks", json={"title": "Buy milk", "due_date": due_date})
    assert response.status_code == 422
    assert ["body", "due_date"] in [entry["loc"] for entry in response.json()["detail"]]
    listed = tasks_client.get("/tasks")
    assert listed.status_code == 200
    assert listed.json() == []


def test_ac_001_5_list_returns_created_tasks_oldest_first(  # AC-001.5
    tasks_client: TestClient,
) -> None:
    created = [
        tasks_client.post("/tasks", json={"title": "First"}).json(),
        tasks_client.post("/tasks", json={"title": "Second", "due_date": "2026-12-31"}).json(),
        tasks_client.post("/tasks", json={"title": "Third"}).json(),
    ]
    response = tasks_client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == created
    assert [task["title"] for task in response.json()] == ["First", "Second", "Third"]


def test_ac_001_6_list_is_empty_initially(tasks_client: TestClient) -> None:  # AC-001.6
    response = tasks_client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_ac_001_7_duplicate_titles_get_different_ids(tasks_client: TestClient) -> None:  # AC-001.7
    first = tasks_client.post("/tasks", json={"title": "Buy milk"})
    second = tasks_client.post("/tasks", json={"title": "Buy milk"})
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] != second.json()["id"]
    listed = tasks_client.get("/tasks").json()
    assert listed == [first.json(), second.json()]
