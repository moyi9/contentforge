"""ContentForge LangGraph workflow — 4-agent pipeline.

Flow: START → planner → writer → reviewer → exporter → END
                ↑                    ↓                    │
                └────── rewrite ─────┘                    │
                └────── pass ─────────────────────────────┘
"""

from __future__ import annotations

from typing import Any, Dict, Literal

from langgraph.graph import END, StateGraph

from app.graph.state import AgentState


# ---------------------------------------------------------------------------
# Node stubs — each receives the full state and returns a partial update.
# ---------------------------------------------------------------------------


def planner_node(state: AgentState) -> Dict[str, Any]:
    """Entry-point node.  Sets initial plan and advances to writer."""
    return {
        "current_agent": "planner",
        "progress": 0.0,
        **state,
    }


def writer_node(state: AgentState) -> Dict[str, Any]:
    """Generates article(s) from the plan."""
    return {
        "current_agent": "writer",
        "progress": 0.5,
        **state,
    }


def reviewer_node(state: AgentState) -> Dict[str, Any]:
    """Reviews the draft articles and produces a review result."""
    return {
        "current_agent": "reviewer",
        "progress": 0.75,
        **state,
    }


def exporter_node(state: AgentState) -> Dict[str, Any]:
    """Exports the final articles to target platforms."""
    return {
        "current_agent": "exporter",
        "progress": 1.0,
        **state,
    }


# ---------------------------------------------------------------------------
# Conditional routing
# ---------------------------------------------------------------------------


def decide_after_review(state: AgentState) -> Literal["pass", "rewrite"]:
    """Route after the reviewer node.

    Returns:
        "pass"    → proceed to exporter (review passed).
        "rewrite" → loop back to writer (fix issues).
    """
    review = state.get("review")
    if review and review.get("passed"):
        return "pass"
    return "rewrite"


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------


def create_workflow() -> StateGraph:
    """Build and **compile** the 4-agent ContentForge workflow.

    Returns a compiled ``StateGraph`` ready for ``.invoke()``.
    """

    builder = StateGraph(AgentState)

    # -- nodes ------------------------------------------------------------------
    builder.add_node("planner", planner_node)
    builder.add_node("writer", writer_node)
    builder.add_node("reviewer", reviewer_node)
    builder.add_node("exporter", exporter_node)

    # -- edges ------------------------------------------------------------------
    builder.set_entry_point("planner")

    # planner → writer → reviewer
    builder.add_edge("planner", "writer")
    builder.add_edge("writer", "reviewer")

    # reviewer → exporter  *or*  reviewer → writer (rewrite loop)
    builder.add_conditional_edges(
        "reviewer",
        decide_after_review,
        {
            "pass": "exporter",
            "rewrite": "writer",
        },
    )

    # exporter → END
    builder.add_edge("exporter", END)

    return builder.compile()
