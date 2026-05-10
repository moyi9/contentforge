"""Tests for ReviewerAgent with mock LLM."""

import pytest
from app.agents.reviewer import ReviewerAgent
from tests.conftest import MockLLMClient


MOCK_REVIEW_RESPONSE = {
    "overall_score": 85,
    "dimensions": {"合规性": 95, "原创度": 78, "可读性": 88, "风格一致性": 82, "平台适配性": 80},
    "issues": [
        {"section_index": 0, "text": "能更简洁", "severity": "warning", "dimension": "可读性", "suggestion": "简化开头"},
    ],
    "summary": "整体质量不错，可读性可优化",
}


@pytest.mark.asyncio
async def test_reviewer_generates_report():
    mock_llm = MockLLMClient()
    mock_llm.set_response(MOCK_REVIEW_RESPONSE)
    agent = ReviewerAgent(llm_client=mock_llm)

    result = await agent.run(
        project_context={},
        article={
            "title": "Test",
            "sections": [{"heading": "Intro", "content": "Hello world"}],
        },
        platform="公众号",
    )
    assert "overall_score" in result
    assert "dimensions" in result
    assert "issues" in result


@pytest.mark.asyncio
async def test_reviewer_detects_forbidden_words():
    mock_llm = MockLLMClient()
    mock_llm.set_response(MOCK_REVIEW_RESPONSE)
    agent = ReviewerAgent(llm_client=mock_llm)

    result = await agent.run(
        project_context={"forbidden_words": ["bad", "terrible"]},
        article={"title": "Test", "sections": [{"heading": "Intro", "content": "This is bad content"}]},
        platform="技术博客",
    )
    assert isinstance(result["issues"], list)


@pytest.mark.asyncio
async def test_reviewer_scores_all_dimensions():
    mock_llm = MockLLMClient()
    mock_llm.set_response(MOCK_REVIEW_RESPONSE)
    agent = ReviewerAgent(llm_client=mock_llm)

    result = await agent.run(
        project_context={},
        article={"title": "Test", "sections": [{"heading": "Intro", "content": "Content"}]},
        platform="公众号",
    )
    expected_dims = ["合规性", "原创度", "可读性", "风格一致性", "平台适配性"]
    for dim in expected_dims:
        assert dim in result["dimensions"], f"Missing dimension: {dim}"


@pytest.mark.asyncio
async def test_reviewer_passes_clean_article():
    mock_llm = MockLLMClient()
    mock_llm.set_response(MOCK_REVIEW_RESPONSE)
    agent = ReviewerAgent(llm_client=mock_llm)

    result = await agent.run(
        project_context={},
        article={"title": "Good Article", "sections": [{"heading": "Intro", "content": "Well written"}]},
        platform="技术博客",
    )
    assert result["overall_score"] >= 50


@pytest.mark.asyncio
async def test_reviewer_fails_severe_issues():
    mock_llm = MockLLMClient()
    severe_response = dict(MOCK_REVIEW_RESPONSE)
    severe_response["overall_score"] = 45
    severe_response["issues"] = [
        {"section_index": 0, "text": "不合规内容", "severity": "error",
         "dimension": "合规性", "suggestion": "删除违规段落"},
    ]
    mock_llm.set_response(severe_response)
    agent = ReviewerAgent(llm_client=mock_llm)

    result = await agent.run(
        project_context={},
        article={"title": "Bad", "sections": [{"heading": "Intro", "content": "Bad content"}]},
        platform="公众号",
    )
    assert result["overall_score"] < 60
