"""SQLite database connection and schema management.

Uses stdlib sqlite3. No ORM.
"""

import sqlite3
import re
from contextlib import contextmanager

_database_path: str = ""


def _parse_db_url(db_url: str) -> str:
    """Extract the file path from a sqlite:/// URL."""
    match = re.match(r"^sqlite:///(.+)$", db_url)
    if not match:
        raise ValueError(f"Unsupported database URL: {db_url}. Expected sqlite:///...")
    return match.group(1)


def init_db(db_url: str) -> None:
    """Initialize database connection and create tables."""
    global _database_path
    _database_path = _parse_db_url(db_url)

    conn = sqlite3.connect(_database_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            writing_style TEXT DEFAULT '',
            forbidden_words TEXT DEFAULT '[]',
            template_config TEXT DEFAULT '{}',
            knowledge_base_path TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_docs (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            title TEXT,
            content TEXT,
            doc_type TEXT,
            source_path TEXT,
            chunk_ids TEXT DEFAULT '[]',
            indexed_at TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)
    conn.commit()
    conn.close()


@contextmanager
def get_db():
    """Context manager that yields a dict-row connection to the database."""
    if not _database_path:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    conn = sqlite3.connect(_database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
