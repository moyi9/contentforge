"""Project CRUD API endpoints."""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.db.projects import (
    create_project,
    delete_project,
    get_project,
    list_projects,
    update_project,
)

router = APIRouter()


@router.post("")
def api_create_project(data: dict):
    project_id = str(uuid.uuid4())[:8]
    data["id"] = project_id
    data["created_at"] = datetime.now(tz=timezone.utc).isoformat()
    data["forbidden_words"] = str(data.get("forbidden_words", []))
    data["template_config"] = str(data.get("template_config", {}))
    data["knowledge_base_path"] = data.get("knowledge_base_path", "")

    create_project(data)

    p = get_project(project_id)
    if not p:
        raise HTTPException(500, "Failed to create project")
    return p


@router.get("")
def api_list_projects():
    return list_projects()


@router.get("/{project_id}")
def api_get_project(project_id: str):
    p = get_project(project_id)
    if not p:
        raise HTTPException(404, "Project not found")
    return p


@router.delete("/{project_id}")
def api_delete_project(project_id: str):
    deleted = delete_project(project_id)
    if not deleted:
        raise HTTPException(404, "Project not found")
    return {"status": "deleted", "id": project_id}
