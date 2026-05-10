"""Article and export API endpoints."""

import asyncio
import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.agents.exporter import ExporterAgent
from app.db.database import get_db
from app.db.projects import create_article, get_article

router = APIRouter()


@router.post("")
def api_submit_article(data: dict):
    """Create a new article from task output sections."""
    article_id = str(uuid.uuid4())[:8]
    data["id"] = article_id
    data["rag_sources"] = json.dumps(data.get("rag_sources", []))
    data["image_suggestions"] = json.dumps(data.get("image_suggestions", []))
    data["metadata"] = json.dumps(data.get("metadata", {}))
    data["sections"] = json.dumps(data.get("sections", []))
    data["created_at"] = datetime.now(tz=timezone.utc).isoformat()

    with get_db() as db:
        create_article(db, data)

    with get_db() as db:
        a = get_article(db, article_id)
    # Parse JSON-encoded fields back to Python objects
    for field in ("sections", "rag_sources", "image_suggestions", "metadata"):
        if isinstance(a.get(field), str):
            try:
                a[field] = json.loads(a[field])
            except (json.JSONDecodeError, TypeError):
                pass
    return a


@router.get("/{article_id}")
def api_get_article(article_id: str):
    """Get a single article by id."""
    with get_db() as db:
        a = get_article(db, article_id)
    if not a:
        raise HTTPException(404, "Article not found")

    # Parse JSON-encoded fields back to Python objects
    for field in ("sections", "rag_sources", "image_suggestions", "metadata"):
        if isinstance(a.get(field), str):
            try:
                a[field] = json.loads(a[field])
            except (json.JSONDecodeError, TypeError):
                pass
    return a


@router.post("/{article_id}/export")
def api_export_article(article_id: str, data: dict):
    """Export an article to the requested format."""
    with get_db() as db:
        a = get_article(db, article_id)
    if not a:
        raise HTTPException(404, "Article not found")

    sections = (
        json.loads(a["sections"])
        if isinstance(a["sections"], str)
        else a["sections"]
    )

    article_for_export = {
        "title": a["title"],
        "sections": sections,
    }

    exporter = ExporterAgent()
    result = asyncio.run(
        exporter.run(
            article=article_for_export,
            format=data.get("format", "markdown"),
            include_review_notes=data.get("include_review_notes", False),
            include_image_suggestions=data.get("include_image_suggestions", True),
        )
    )
    return result
