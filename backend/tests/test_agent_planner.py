"""Tests for PlannerAgent with mock LLM."""

import pytest
from app.agents.planner import PlannerAgent
from tests.conftest import MockLLMClient


MOCK_PLANNER_RESPONSE = {
    "candidates": [
        {"title": "AI Agent Development: A Complete Guide",
         "outline": ["Introduction", "Core Concepts", "Implementation", "Best Practices", "Conclusion"],
         "score": 9.0},
        {"title": "Building Your First AI Agent",
         "outline": ["Getting Started", "Tools & Frameworks", "Step-by-Step", "Deployment"],
         "score": 8.0},
        {"title": "AI Agents in 2026: Trends & Predictions",
         "outline": ["Current Landscape", "Emerging Trends", "Future Outlook"],
         "score": 7.5},
    ],
    "analysis": "选题覆盖从入门到趋势，适配开发者群体",
}


@pytest.mark.asyncio
async def test_planner_generates_candidates():
    mock_llm = MockLLMClient()
    mock_llm.set_response(MOCK_PLANNER_RESPONSE)
    agent = PlannerAgent(llm_client=mock_llm)

    result = await agent.run(
        project_context={"writing_style": "technical, concise", "name": "Tech Blog"},
        topic="AI Agent development",
        platform="公众号",
        target_audience="developers",
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
    mock_llm = MockLLMClient()
    mock_llm.set_response(MOCK_PLANNER_RESPONSE)
    agent = PlannerAgent(llm_client=mock_llm)

    result = await agent.run(
        project_context={},
        topic="AI",
        platform="技术博客",
        target_audience="devs",
    )
    scores = [c["score"] for c in result["candidates"]]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_planner_respects_platform():
    mock_llm = MockLLMClient()
    mock_llm.set_response(MOCK_PLANNER_RESPONSE)
    agent = PlannerAgent(llm_client=mock_llm)

    result = await agent.run(
        project_context={},
        topic="Python",
        platform="知乎",
        target_audience="students",
    )
    assert result["platform"] == "知乎"
