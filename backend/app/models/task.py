from typing import Literal, Optional

from pydantic import BaseModel, Field


class TaskRequest(BaseModel):
    project_id: str
    topic: str
    platforms: list[str]
    content_type: str
    target_audience: str
    word_count: int = Field(default=1000, ge=1)
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
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    result: Optional[dict] = None
    error: Optional[str] = None
