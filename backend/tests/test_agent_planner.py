import pytest
from app.agents.planner import PlannerAgent


@pytest.mark.asyncio
async def test_planner_generates_candidates():
    agent = PlannerAgent()
    result = await agent.run(
        project_context={
            "writing_style": "technical, concise",
            "template_config": {}
        },
        topic="AI Agent development",
        platform="公众号",
        target_audience="developers"
    )
    assert "candidates" in result
    assert isinstance(result["candidates"], list)
    assert len(result["candidates"]) >= 1
    for c in result["candidates"]:
        assert "title" in c
        assert "outline" in c
        assert "score" in c


@pytest.mark.asyncio
async def test_planner_ranks_by_score():
    agent = PlannerAgent()
    result = await agent.run(
        project_context={"writing_style": "casual", "template_config": {}},
        topic="AI trends in 2026",
        platform="小红书",
        target_audience="young professionals"
    )
    candidates = result["candidates"]
    scores = [c["score"] for c in candidates]
    # Scores should be descending (sorted best first)
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_planner_respects_platform():
    agent = PlannerAgent()
    result = await agent.run(
        project_context={"writing_style": "casual", "template_config": {"小红书": "hook + story + tip"}},
        topic="health tips",
        platform="小红书",
        target_audience="general"
    )
    assert len(result["candidates"]) >= 1
