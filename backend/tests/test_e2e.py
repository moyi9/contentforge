"""End-to-end integration tests for ContentForge API.

Tests each major API domain (projects, knowledge, tasks, articles) in sequence
using a dedicated temporary SQLite database. Each test function is independent
and uses a shared client fixture seeded with a default project.
"""
import tempfile
import os
import json
import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.db.database import init_db, get_db
from app.db.projects import create_project, create_knowledge_doc, create_task


@pytest.fixture
def client():
    """Fixture: isolated SQLite database + seed project for E2E tests."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    init_db(f"sqlite:///{db_path}")

    # Seed a project for knowledge/task/article tests
    create_project({
        "id": "e2e-proj",
        "name": "E2E Test",
        "description": "",
        "writing_style": "tech",
        "forbidden_words": "[]",
        "template_config": "{}",
        "knowledge_base_path": "",
    })

    # Seed a task for article tests
    with get_db() as db:
        create_task(db, {
            "id": "e2e-task",
            "project_id": "e2e-proj",
            "topic": "E2E Topic",
            "platforms": str(["公众号"]),
            "content_type": "tech",
            "target_audience": "developers",
            "word_count": 500,
            "state": "done",
            "current_agent": "writer",
            "progress": 100.0,
            "created_at": "2026-01-01T00:00:00",
        })

    with TestClient(app) as c:
        yield c

    os.remove(db_path)


# ── Project lifecycle ────────────────────────────────────────────────────────


def test_e2e_project_lifecycle(client):
    """Create, list, get, and delete a project."""
    # Create
    resp = client.post("/api/projects", json={
        "name": "E2E Blog",
        "description": "End-to-end test",
        "writing_style": "technical",
        "forbidden_words": ["bad", "terrible"],
        "template_config": {},
        "knowledge_base_path": "./vault/e2e",
    })
    assert resp.status_code == 200
    pid = resp.json()["id"]
    assert resp.json()["name"] == "E2E Blog"

    # List
    resp = client.get("/api/projects")
    assert resp.status_code == 200
    assert len(resp.json()) > 0

    # Get
    resp = client.get(f"/api/projects/{pid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == pid

    # Delete
    resp = client.delete(f"/api/projects/{pid}")
    assert resp.status_code == 200

    # Verify deleted
    resp = client.get(f"/api/projects/{pid}")
    assert resp.status_code == 404


# ── Knowledge management ──────────────────────────────────────────────────────


def test_e2e_knowledge_upload(client):
    """Upload and list knowledge documents."""
    # Upload
    resp = client.post("/api/knowledge/upload", json={
        "project_id": "e2e-proj",
        "title": "Style Guide",
        "content": "# Style Guide\n\nKeep it technical and concise.",
        "doc_type": "style_guide",
        "source_path": "style.md",
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

    # List
    resp = client.get("/api/knowledge/e2e-proj")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


# ── Task lifecycle ────────────────────────────────────────────────────────────


def test_e2e_task_lifecycle(client):
    """Create, get, and list tasks."""
    # Create
    resp = client.post("/api/tasks", json={
        "project_id": "e2e-proj",
        "topic": "E2E Test Topic",
        "platforms": ["公众号"],
        "content_type": "technical",
        "target_audience": "developers",
        "word_count": 500,
    })
    assert resp.status_code == 200
    tid = resp.json()["id"]
    assert resp.json()["state"] == "pending"

    # Get
    resp = client.get(f"/api/tasks/{tid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == tid

    # List
    resp = client.get("/api/tasks")
    assert resp.status_code == 200
    assert len(resp.json()) > 0


# ── Article & Export ──────────────────────────────────────────────────────────


def test_e2e_article_export(client):
    """Create an article and export it to markdown."""
    # Create article
    resp = client.post("/api/articles", json={
        "task_id": "e2e-task",
        "platform": "公众号",
        "title": "E2E Article",
        "sections": [{"heading": "Intro", "content": "Test content", "rag_ref": None}],
    })
    assert resp.status_code == 200
    aid = resp.json()["id"]
    assert resp.json()["title"] == "E2E Article"

    # Get
    resp = client.get(f"/api/articles/{aid}")
    assert resp.status_code == 200
    sections = resp.json()["sections"]
    assert isinstance(sections, list)
    assert len(sections) > 0

    # Export
    resp = client.post(f"/api/articles/{aid}/export", json={
        "format": "markdown",
        "include_review_notes": False,
        "include_image_suggestions": False,
    })
    assert resp.status_code == 200
    assert resp.json()["format"] == "markdown"
    assert "file_path" in resp.json()
