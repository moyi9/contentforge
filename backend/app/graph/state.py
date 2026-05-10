"""AgentState — the shared TypedDict for the ContentForge LangGraph workflow."""

from typing import Any, Dict, List, Optional, TypedDict


class ReviewResult(TypedDict, total=False):
    """Result from the reviewer agent."""

    passed: bool
    overall_score: float
    dimensions: Dict[str, float]
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    requires_full_rewrite: bool
    baseline_comparison: Dict[str, Any]


class PlanDict(TypedDict, total=False):
    """Structure of a content plan produced by the planner."""

    sections: List[Dict[str, Any]]
    key_points: List[str]
    tone: str
    estimated_word_count: int


class AgentState(TypedDict, total=False):
    """Shared state passed through every node in the ContentForge pipeline.

    All fields are optional at the type level because LangGraph's StateGraph
    merges partial updates at each node.  In practice the planner is always
    the entry point and populates the majority of fields.
    """

    # -- identity ----------------------------------------------------------------
    task_id: str
    project_id: str
    project_context: Dict[str, Any]

    # -- user request ------------------------------------------------------------
    topic: str
    platforms: List[str]
    content_type: str
    target_audience: str
    word_count: int

    # -- LLM conversation history ------------------------------------------------
    messages: List[Any]

    # -- pipeline bookkeeping ----------------------------------------------------
    current_agent: str
    progress: float
    error: Optional[str]

    # -- agent artefacts ---------------------------------------------------------
    plan: Optional[PlanDict]
    articles: List[Dict[str, Any]]
    review: Optional[ReviewResult]
    export_results: List[Dict[str, Any]]
