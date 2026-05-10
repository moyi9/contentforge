import pytest
from app.graph.state import AgentState
from app.graph.workflow import create_workflow, decide_after_review


def test_agent_state_initialization():
    state = AgentState(
        task_id="task-1",
        project_id="proj-1",
        project_context={"writing_style": "tech"},
        topic="AI Agents",
        platforms=["公众号"],
        content_type="technical",
        target_audience="developers",
        word_count=500,
        messages=[],
        current_agent="planner",
        plan=None,
        articles=[],
        review=None,
        export_results=[],
        progress=0.0,
        error=None,
    )
    assert state["task_id"] == "task-1"
    assert state["project_id"] == "proj-1"
    assert state["platforms"] == ["公众号"]
    assert state["progress"] == 0.0


def test_state_defaults():
    """Test that optional fields have sensible defaults"""
    state = AgentState(
        task_id="task-1",
        project_id="proj-1",
        project_context={},
        topic="AI",
        platforms=["公众号"],
        content_type="tech",
        target_audience="devs",
        word_count=500,
        messages=[],
        current_agent="planner",
        plan=None,
        articles=[],
        review=None,
        export_results=[],
        progress=0.0,
        error=None,
    )
    assert state["plan"] is None
    assert state["articles"] == []
    assert state["error"] is None


def test_decide_after_review_pass():
    """When review passes, should route to exporter"""
    state = AgentState(
        task_id="t1",
        project_id="p1",
        project_context={},
        topic="AI",
        platforms=["公众号"],
        content_type="tech",
        target_audience="devs",
        word_count=500,
        messages=[],
        current_agent="reviewer",
        plan=None,
        articles=[],
        review={
            "passed": True,
            "overall_score": 85,
            "dimensions": {},
            "issues": [],
            "suggestions": [],
            "baseline_comparison": {},
        },
        export_results=[],
        progress=0.8,
        error=None,
    )
    result = decide_after_review(state)
    assert result == "pass"


def test_decide_after_review_fail():
    """When review fails, should route back to writer"""
    state = AgentState(
        task_id="t1",
        project_id="p1",
        project_context={},
        topic="AI",
        platforms=["公众号"],
        content_type="tech",
        target_audience="devs",
        word_count=500,
        messages=[],
        current_agent="reviewer",
        plan=None,
        articles=[],
        review={
            "passed": False,
            "overall_score": 40,
            "dimensions": {},
            "issues": [],
            "suggestions": [],
            "requires_full_rewrite": True,
            "baseline_comparison": {},
        },
        export_results=[],
        progress=0.7,
        error=None,
    )
    result = decide_after_review(state)
    assert result == "rewrite"


def test_workflow_creation():
    """Workflow should be creatable with nodes"""
    workflow = create_workflow()
    assert workflow is not None
