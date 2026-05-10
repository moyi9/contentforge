from typing import Literal

from pydantic import BaseModel


class ReviewIssue(BaseModel):
    section_index: int
    text: str
    severity: Literal["error", "warning", "info"]
    dimension: str
    rule_ref: str
    suggestion: str
    auto_fixed: bool = False


class ReviewResult(BaseModel):
    article_id: str
    overall_score: float
    dimensions: dict[str, float]
    baseline_comparison: dict
    issues: list[ReviewIssue]
    suggestions: list[str]
    passed: bool
