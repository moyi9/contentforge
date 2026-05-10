"""CRUD operations for the projects table."""

from app.db.database import get_db


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


def update_project(project_id: str, data: dict) -> None:
    """Update fields of an existing project."""
    assignments = ", ".join(f"{k} = :{k}" for k in data)
    params = {**data, "id": project_id}
    with get_db() as db:
        db.execute(
            f"UPDATE projects SET {assignments} WHERE id = :id",
            params,
        )


def delete_project(project_id: str) -> None:
    """Delete a project by id."""
    with get_db() as db:
        db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
