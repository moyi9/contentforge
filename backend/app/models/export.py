from typing import Literal

from pydantic import BaseModel


class ExportRequest(BaseModel):
    article_id: str
    format: Literal["pdf", "markdown", "rich_text", "plain_text"]
    include_review_notes: bool = False
    include_image_suggestions: bool = True
