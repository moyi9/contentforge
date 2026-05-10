from typing import Literal, Optional

from pydantic import BaseModel


class TaskRequest(BaseModel):
    project_id: str
    topic: str
    platforms: list[str]
    content_type: str
    target_audience: str
    word_count: int = 1000
    tone_override: Optional[str] = None


class TaskStatus(BaseModel):
    task_id: str
    state: Literal[
        "pending",
        "planning",
        "awaiting_plan",
        "writing",
        "awaiting_draft",
        "reviewing",
        "awaiting_review",
        "exporting",
        "done",
        "failed",
    ]
    current_agent: str
    progress: float = 0.0
    result: Optional[dict] = None
    error: Optional[str] = None
