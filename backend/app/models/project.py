from datetime import datetime

from pydantic import BaseModel, Field


class Project(BaseModel):
    id: str
    name: str
    description: str
    writing_style: str
    forbidden_words: list[str]
    template_config: dict
    knowledge_base_path: str
    created_at: datetime = Field(default_factory=datetime.now)
