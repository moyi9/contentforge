from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class KnowledgeDoc(BaseModel):
    id: str
    project_id: str
    title: str
    content: str
    doc_type: Literal["style_guide", "reference", "rule", "template", "past_work"]
    source_path: str
    chunk_ids: list[str]
    indexed_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
