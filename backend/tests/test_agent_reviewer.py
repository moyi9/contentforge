import pytest
from app.agents.reviewer import ReviewerAgent

SAMPLE_ARTICLE = {
    "title": "AI Guide",
    "sections": [
        {"heading": "Intro", "content": "AI is great and we should use it. It helps with stuff.", "rag_ref": None},
        {"heading": "Body", "content": "More content here about AI agents and how they work.", "rag_ref": "doc-1"}
    ]
}


@pytest.mark.asyncio
async def test_reviewer_generates_report():
    agent = ReviewerAgent()
    result = await agent.run(
        article=SAMPLE_ARTICLE,
        project_context={
            "writing_style": "technical, detailed",
            "forbidden_words": ["great", "stuff"]
        }
    )
    assert "overall_score" in result
    assert 0 <= result["overall_score"] <= 100
    assert "dimensions" in result
    assert isinstance(result["dimensions"], dict)
    assert "issues" in result
    assert isinstance(result["issues"], list)
    assert "suggestions" in result
    assert "passed" in result


@pytest.mark.asyncio
async def test_reviewer_detects_forbidden_words():
    agent = ReviewerAgent()
    result = await agent.run(
        article=SAMPLE_ARTICLE,
        project_context={
            "writing_style": "technical",
            "forbidden_words": ["great", "stuff"]
        }
    )
    forbidden_issues = [
        i for i in result["issues"]
        if i["dimension"] == "合规性"
    ]
    assert len(forbidden_issues) > 0
    # Each forbidden word issue should reference the specific word
    for issue in forbidden_issues:
        assert issue["suggestion"] != ""


@pytest.mark.asyncio
async def test_reviewer_scores_all_dimensions():
    agent = ReviewerAgent()
    result = await agent.run(
        article=SAMPLE_ARTICLE,
        project_context={"writing_style": "concise", "forbidden_words": []}
    )
    dims = result["dimensions"]
    expected_dims = {"合规性", "原创度", "可读性", "风格一致性", "平台适配性"}
    for dim in expected_dims:
        assert dim in dims
        assert 0 <= dims[dim] <= 100


@pytest.mark.asyncio
async def test_reviewer_passes_clean_article():
    """An article without forbidden words should pass"""
    clean_article = {
        "title": "Clean Post",
        "sections": [
            {"heading": "Intro", "content": "A well-written introduction about technology.", "rag_ref": None}
        ]
    }
    agent = ReviewerAgent()
    result = await agent.run(
        article=clean_article,
        project_context={"writing_style": "technical", "forbidden_words": ["spam", "scam"]}
    )
    assert result["passed"] is True


@pytest.mark.asyncio
async def test_reviewer_fails_severe_issues():
    """An article with severe issues should fail review"""
    bad_article = {
        "title": "Bad",
        "sections": [
            {"heading": "Intro", "content": "Buy now!!! spam spam spam scam limited offer click here!!!", "rag_ref": None}
        ]
    }
    agent = ReviewerAgent()
    result = await agent.run(
        article=bad_article,
        project_context={
            "writing_style": "professional",
            "forbidden_words": ["spam", "scam", "buy now", "click here"]
        }
    )
    assert result["passed"] is False
