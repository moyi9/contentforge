import pytest
import sqlite3
import os
from app.db.database import get_db, init_db
from app.db.projects import (
    create_project,
    get_project,
    list_projects,
    update_project,
    delete_project,
)


@pytest.fixture
def test_db():
    """Create a fresh test database for each test"""
    db_path = "/tmp/contentforge_test.db"
    # Clean up any previous test db
    if os.path.exists(db_path):
        os.remove(db_path)
    init_db(f"sqlite:///{db_path}")
    return db_path


def test_create_and_get_project(test_db):
    project_data = {
        "id": "proj-1",
        "name": "Test Project",
        "description": "A test project",
        "writing_style": "casual",
        "forbidden_words": "[]",
        "template_config": "{}",
        "knowledge_base_path": "./vault/test",
    }
    create_project(project_data)
    p = get_project("proj-1")
    assert p is not None
    assert p["name"] == "Test Project"
    assert p["writing_style"] == "casual"
    assert p["id"] == "proj-1"


def test_list_projects(test_db):
    create_project(
        {
            "id": "p1",
            "name": "A",
            "description": "",
            "writing_style": "",
            "forbidden_words": "[]",
            "template_config": "{}",
            "knowledge_base_path": "",
        }
    )
    create_project(
        {
            "id": "p2",
            "name": "B",
            "description": "",
            "writing_style": "",
            "forbidden_words": "[]",
            "template_config": "{}",
            "knowledge_base_path": "",
        }
    )
    projects = list_projects()
    assert len(projects) == 2
    names = {p["name"] for p in projects}
    assert names == {"A", "B"}


def test_delete_project(test_db):
    create_project(
        {
            "id": "p1",
            "name": "To Delete",
            "description": "",
            "writing_style": "",
            "forbidden_words": "[]",
            "template_config": "{}",
            "knowledge_base_path": "",
        }
    )
    delete_project("p1")
    assert get_project("p1") is None


def test_update_project(test_db):
    create_project(
        {
            "id": "p1",
            "name": "Original",
            "description": "",
            "writing_style": "",
            "forbidden_words": "[]",
            "template_config": "{}",
            "knowledge_base_path": "",
        }
    )
    update_project("p1", {"name": "Updated", "writing_style": "formal"})
    p = get_project("p1")
    assert p["name"] == "Updated"
    assert p["writing_style"] == "formal"


def test_get_nonexistent_project(test_db):
    assert get_project("nonexistent") is None


def test_update_project_empty_data(test_db):
    create_project({
        "id": "p1",
        "name": "Test",
        "description": "",
        "writing_style": "",
        "forbidden_words": "[]",
        "template_config": "{}",
        "knowledge_base_path": "",
    })
    with pytest.raises(ValueError, match="must not be empty"):
        update_project("p1", {})


def test_update_project_invalid_column(test_db):
    create_project({
        "id": "p1",
        "name": "Test",
        "description": "",
        "writing_style": "",
        "forbidden_words": "[]",
        "template_config": "{}",
        "knowledge_base_path": "",
    })
    with pytest.raises(ValueError, match="invalid column"):
        update_project("p1", {"name": "ok", "evil_column": "drop table"})


def test_update_project_nonexistent(test_db):
    affected = update_project("ghost", {"name": "No One"})
    assert affected == 0


def test_duplicate_insert(test_db):
    data = {
        "id": "p1",
        "name": "First",
        "description": "",
        "writing_style": "",
        "forbidden_words": "[]",
        "template_config": "{}",
        "knowledge_base_path": "",
    }
    create_project(data)
    with pytest.raises(sqlite3.IntegrityError):
        create_project(data)
