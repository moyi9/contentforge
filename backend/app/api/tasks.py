"""Task management API with SSE progress."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.db.database import get_db
from app.db.projects import create_task, get_task, list_tasks

router = APIRouter()


@router.post("")
def api_create_task(data: dict):
    task_id = str(uuid.uuid4())
    data["id"] = task_id
    data["created_at"] = datetime.now(tz=timezone.utc).isoformat()
    data["platforms"] = str(data.get("platforms", []))
    data["state"] = "pending"
    data["current_agent"] = "planner"
    data["progress"] = 0.0

    with get_db() as db:
        create_task(db, data)
        t = get_task(db, task_id)

    if not t:
        raise HTTPException(500, "Failed to create task")
    return t


@router.get("")
def api_list_tasks():
    with get_db() as db:
        return list_tasks(db)


@router.get("/{task_id}")
def api_get_task(task_id: str):
    with get_db() as db:
        t = get_task(db, task_id)
    if not t:
        raise HTTPException(404, "Task not found")
    return t
