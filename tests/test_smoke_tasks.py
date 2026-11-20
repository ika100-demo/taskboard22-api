"""Smoke tests for spec 001 (AC-001.1, AC-001.5): create and list tasks through the base URL.

They reach the service only through its URL and create uniquely named tasks (`smoke-<uuid>`).
They create data, so they carry `@pytest.mark.writes` and run only in dev (#474). Tasks cannot
be deleted (non-goal), so they only ever look at the tasks they created themselves.
"""

from __future__ import annotations

import json
import urllib.request
import uuid
from typing import Any

import pytest


def _request(url: str, payload: dict[str, Any] | None = None) -> tuple[int, Any]:
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(  # noqa: S310
        url, data=data, headers={"Content-Type": "application/json"} if data else {}
    )
    with urllib.request.urlopen(req, timeout=10) as response:  # noqa: S310
        return response.status, json.load(response)


@pytest.mark.smoke
@pytest.mark.writes
def test_ac_001_1_smoke_create_task(smoke_base_url: str) -> None:  # AC-001.1
    title = f"smoke-{uuid.uuid4()}"
    status, body = _request(smoke_base_url + "/tasks", {"title": title})
    assert status == 201
    assert isinstance(body["id"], str)
    assert body["id"] != ""
    assert body["title"] == title
    assert body["due_date"] is None


@pytest.mark.smoke
@pytest.mark.writes
def test_ac_001_5_smoke_list_contains_created_task(smoke_base_url: str) -> None:  # AC-001.5
    title = f"smoke-{uuid.uuid4()}"
    _, created = _request(smoke_base_url + "/tasks", {"title": title})
    status, tasks = _request(smoke_base_url + "/tasks")
    assert status == 200
    assert isinstance(tasks, list)
    assert [task for task in tasks if task["id"] == created["id"]] == [created]
