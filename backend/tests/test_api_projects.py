"""Tests for the FastAPI projects API endpoints."""
import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.db.database import init_db


@pytest.fixture
def client(tmp_path):
    """Fixture: TestClient with isolated temp SQLite database."""
    db_path = tmp_path / "test_contentforge.db"
    init_db(f"sqlite:///{db_path}")
    with TestClient(app) as c:
        yield c


def test_create_project(client):
    resp = client.post(
        "/api/projects",
        json={
            "name": "My Blog",
            "description": "Personal tech blog",
            "writing_style": "casual",
            "forbidden_words": [],
            "template_config": {},
            "knowledge_base_path": "./vault/blog",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "My Blog"
    assert "id" in data
    assert "created_at" in data


def test_list_projects(client):
    """Should start empty, then reflect created projects."""
    resp = client.get("/api/projects")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_project(client):
    create_resp = client.post(
        "/api/projects",
        json={
            "name": "Test",
            "description": "desc",
            "writing_style": "",
            "forbidden_words": [],
            "template_config": {},
            "knowledge_base_path": "",
        },
    )
    pid = create_resp.json()["id"]

    resp = client.get(f"/api/projects/{pid}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Test"


def test_get_nonexistent_project(client):
    resp = client.get("/api/projects/nonexistent")
    assert resp.status_code == 404


def test_delete_project(client):
    create_resp = client.post(
        "/api/projects",
        json={
            "name": "To Delete",
            "description": "",
            "writing_style": "",
            "forbidden_words": [],
            "template_config": {},
            "knowledge_base_path": "",
        },
    )
    pid = create_resp.json()["id"]

    resp = client.delete(f"/api/projects/{pid}")
    assert resp.status_code == 200

    resp = client.get(f"/api/projects/{pid}")
    assert resp.status_code == 404
