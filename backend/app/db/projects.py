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


def delete_project(project_id: str) -> int:
    """Delete a project by id. Returns the number of affected rows."""
    with get_db() as db:
        cursor = db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        return cursor.rowcount
