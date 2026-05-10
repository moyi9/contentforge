from typing import Optional

from pydantic import BaseModel


class Section(BaseModel):
    heading: str
    content: str
    rag_ref: Optional[str] = None


class ImageSuggestion(BaseModel):
    description: str
    unsplash_url: Optional[str] = None
    section_index: int


class Article(BaseModel):
    id: str
    task_id: str
    platform: str
    title: str
    sections: list[Section]
    image_suggestions: list[ImageSuggestion]
    rag_sources: list[str]
    metadata: dict
