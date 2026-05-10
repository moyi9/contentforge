"""Tests for knowledge management API endpoints."""
import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from app.api.main import app
from app.db.database import init_db
from app.db.projects import create_project


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    init_db(f"sqlite:///{db_path}")

    # Create test projects (create_project manages its own connection)
    create_project({
        "id": "proj-1-1", "name": "Test", "description": "",
        "writing_style": "", "forbidden_words": "[]",
        "template_config": "{}", "knowledge_base_path": "",
    })
    create_project({
        "id": "proj-2-1", "name": "Test2", "description": "",
        "writing_style": "", "forbidden_words": "[]",
        "template_config": "{}", "knowledge_base_path": "",
    })

    with TestClient(app) as c:
        yield c

    os.remove(db_path)


def test_upload_document(client):
    resp = client.post("/api/knowledge/upload", json={
        "project_id": "proj-1-1",
        "title": "Style Guide",
        "content": "# Style Guide\n\nBe concise.",
        "doc_type": "style_guide",
        "source_path": "docs/style.md",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_list_knowledge_docs(client):
    # Upload a doc first
    client.post("/api/knowledge/upload", json={
        "project_id": "proj-1-1",
        "title": "Doc1", "content": "Content 1",
        "doc_type": "note", "source_path": "",
    })
    resp = client.get("/api/knowledge/proj-1-1")
    assert resp.status_code == 200
    docs = resp.json()
    assert isinstance(docs, list)
    assert len(docs) == 1


def test_list_knowledge_empty(client):
    resp = client.get("/api/knowledge/proj-2-1")
    assert resp.status_code == 200
    assert resp.json() == []
