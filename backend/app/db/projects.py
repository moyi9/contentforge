"""CRUD operations for the projects table."""

from app.db.database import get_db

ALLOWED_COLUMNS = {
    "name",
    "description",
    "writing_style",
    "forbidden_words",
    "template_config",
    "knowledge_base_path",
}


def create_project(data: dict) -> None:
    """Insert a new project."""
    with get_db() as db:
        db.execute(
            """INSERT INTO projects (id, name, description, writing_style,
               forbidden_words, template_config, knowledge_base_path)
               VALUES (:id, :name, :description, :writing_style,
               :forbidden_words, :template_config, :knowledge_base_path)""",
            data,
        )


def get_project(project_id: str) -> dict | None:
    """Get a single project by id. Returns dict or None."""
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
    if row is None:
        return None
    return dict(row)


def list_projects() -> list[dict]:
    """List all projects."""
    with get_db() as db:
        rows = db.execute("SELECT * FROM projects").fetchall()
    return [dict(row) for row in rows]


def update_project(project_id: str, data: dict) -> int:
    """Update fields of an existing project.

    Returns the number of affected rows (0 if project did not exist).
    Raises ValueError if data is empty or contains invalid column names.
    """
    if not data:
        raise ValueError("update data must not be empty")
    invalid = set(data) - ALLOWED_COLUMNS
    if invalid:
        raise ValueError(f"invalid column(s): {', '.join(sorted(invalid))}")
    assignments = ", ".join(f"{k} = :{k}" for k in data)
    params = {**data, "id": project_id}
    with get_db() as db:
        cursor = db.execute(
            f"UPDATE projects SET {assignments} WHERE id = :id",
            params,
        )
        return cursor.rowcount


def create_knowledge_doc(db, data: dict) -> None:
    """Insert a new knowledge document."""
    db.execute(
        """INSERT INTO knowledge_docs
           (id, project_id, title, content, doc_type, source_path, chunk_ids, indexed_at)
           VALUES (:id, :project_id, :title, :content, :doc_type, :source_path, :chunk_ids, :indexed_at)""",
        data,
    )


def list_knowledge_docs(db, project_id: str) -> list[dict]:
    """List all knowledge docs for a project."""
    rows = db.execute(
        "SELECT * FROM knowledge_docs WHERE project_id = ?", (project_id,)
    ).fetchall()
    return [dict(row) for row in rows]


def delete_project(project_id: str) -> int:
    """Delete a project by id. Returns the number of affected rows."""
    with get_db() as db:
        cursor = db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        return cursor.rowcount


TASK_ALLOWED_COLUMNS = {
    "id", "project_id", "topic", "content_type", "target_audience",
    "word_count", "platforms", "state", "current_agent", "progress",
    "created_at",
}


def create_task(db, data: dict) -> None:
    """Insert a new task row using an existing db connection.

    Only columns in TASK_ALLOWED_COLUMNS are accepted; any other keys
    are silently ignored to prevent SQL injection via column names.
    """
    safe = {k: v for k, v in data.items() if k in TASK_ALLOWED_COLUMNS}
    columns = ", ".join(safe.keys())
    placeholders = ", ".join(f":{k}" for k in safe.keys())
    db.execute(f"INSERT INTO tasks ({columns}) VALUES ({placeholders})", safe)
    db.commit()


def get_task(db, task_id: str) -> dict | None:
    """Get a single task by id. Returns dict or None."""
    row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return dict(row) if row else None


def list_tasks(db) -> list[dict]:
    """List all tasks ordered by creation time (newest first)."""
    rows = db.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


ARTICLE_ALLOWED_COLUMNS = {
    "id", "task_id", "platform", "title", "sections",
    "rag_sources", "image_suggestions", "metadata", "created_at",
}


def create_article(db, data: dict) -> None:
    """Insert a new article row using an existing db connection.

    Only columns in ARTICLE_ALLOWED_COLUMNS are accepted; any other keys
    are silently ignored to prevent SQL injection via column names.
    """
    safe = {k: v for k, v in data.items() if k in ARTICLE_ALLOWED_COLUMNS}
    columns = ", ".join(safe.keys())
    placeholders = ", ".join(f":{k}" for k in safe.keys())
    db.execute(f"INSERT INTO articles ({columns}) VALUES ({placeholders})", safe)
    db.commit()


def get_article(db, article_id: str) -> dict | None:
    """Get a single article by id. Returns dict or None."""
    row = db.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
    return dict(row) if row else None
