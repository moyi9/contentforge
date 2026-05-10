"""Knowledge management API — upload and list knowledge documents."""
from fastapi import APIRouter
from app.db.database import get_db
import uuid
from datetime import datetime, timezone

router = APIRouter()


@router.post("/upload")
def api_upload_document(data: dict):
    """Upload a knowledge document."""
    doc_id = str(uuid.uuid4())
    data["id"] = doc_id
    data["indexed_at"] = datetime.now(tz=timezone.utc).isoformat()
    data["chunk_ids"] = str([])

    from app.db.projects import create_knowledge_doc
    with get_db() as db:
        create_knowledge_doc(db, data)
    return {"status": "ok", "doc_id": doc_id}


@router.get("/{project_id}")
def api_list_knowledge(project_id: str):
    """List all knowledge documents for a project."""
    from app.db.projects import list_knowledge_docs
    with get_db() as db:
        return list_knowledge_docs(db, project_id)
