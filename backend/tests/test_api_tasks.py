"""Tests for the FastAPI tasks API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.db.database import init_db
from app.db.projects import create_project


@pytest.fixture
def client(tmp_path):
    """Fixture: TestClient with isolated temp SQLite database."""
    db_path = tmp_path / "test_contentforge.db"
    init_db(f"sqlite:///{db_path}")

    # Create a test project for task tests
    create_project({
        "id": "test-project",
        "name": "Test",
        "description": "",
        "writing_style": "tech",
        "forbidden_words": "[]",
        "template_config": "{}",
        "knowledge_base_path": "",
    })

    with TestClient(app) as c:
        yield c


def test_create_task(client):
    resp = client.post("/api/tasks", json={
        "project_id": "test-project",
        "topic": "AI Agents in 2026",
        "platforms": ["公众号"],
        "content_type": "technical",
        "target_audience": "developers",
        "word_count": 1000,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["state"] == "pending"
    assert "task_id" in data or "id" in data


def test_get_task_status(client):
    create_resp = client.post("/api/tasks", json={
        "project_id": "test-project",
        "topic": "AI Agents",
        "platforms": ["公众号"],
        "content_type": "tech",
        "target_audience": "devs",
        "word_count": 500,
    })
    tid = create_resp.json().get("task_id") or create_resp.json()["id"]

    resp = client.get(f"/api/tasks/{tid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == tid


def test_list_tasks(client):
    resp = client.get("/api/tasks")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_nonexistent_task(client):
    resp = client.get("/api/tasks/nonexistent")
    assert resp.status_code == 404
