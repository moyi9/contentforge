"""Tests for the FastAPI articles and export API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.db.database import init_db, get_db
from app.db.projects import create_project, create_task


@pytest.fixture
def client(tmp_path):
    """Fixture: TestClient with isolated temp SQLite database and seed data."""
    db_path = tmp_path / "test_contentforge.db"
    init_db(f"sqlite:///{db_path}")

    # Seed a project (create_project manages its own db connection)
    create_project({
        "id": "p1",
        "name": "Test",
        "description": "",
        "writing_style": "tech",
        "forbidden_words": "[]",
        "template_config": "{}",
        "knowledge_base_path": "",
    })

    # Seed a task inside a managed db session
    with get_db() as db:
        create_task(db, {
            "id": "t1",
            "project_id": "p1",
            "topic": "AI",
            "platforms": "[]",
            "content_type": "tech",
            "target_audience": "devs",
            "word_count": 500,
            "state": "done",
            "current_agent": "writer",
            "progress": 100.0,
            "created_at": "2026-01-01",
        })

    with TestClient(app) as c:
        yield c


def test_submit_article(client):
    """POST /api/articles should create an article and return it."""
    resp = client.post("/api/articles", json={
        "task_id": "t1",
        "platform": "公众号",
        "title": "AI Guide",
        "sections": [
            {"heading": "Intro", "content": "Hello world", "rag_ref": None},
        ],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "AI Guide"
    assert "id" in data
    assert len(data["sections"]) == 1


def test_get_article(client):
    """GET /api/articles/{id} should return the stored article."""
    create_resp = client.post("/api/articles", json={
        "task_id": "t1",
        "platform": "公众号",
        "title": "Test Article",
        "sections": [{"heading": "Sec1", "content": "Content", "rag_ref": None}],
    })
    aid = create_resp.json()["id"]

    resp = client.get(f"/api/articles/{aid}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Test Article"


def test_export_article(client):
    """POST /api/articles/{id}/export should return a downloadable file path."""
    create_resp = client.post("/api/articles", json={
        "task_id": "t1",
        "platform": "公众号",
        "title": "Export Test",
        "sections": [{"heading": "Sec1", "content": "Content to export", "rag_ref": None}],
    })
    aid = create_resp.json()["id"]

    resp = client.post(f"/api/articles/{aid}/export", json={
        "format": "markdown",
        "include_review_notes": False,
        "include_image_suggestions": False,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["format"] == "markdown"
    assert "file_path" in data


def test_get_nonexistent_article(client):
    """GET /api/articles/nonexistent should return 404."""
    resp = client.get("/api/articles/nonexistent")
    assert resp.status_code == 404
