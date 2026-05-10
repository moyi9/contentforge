import pytest
from app.agents.writer import WriterAgent


@pytest.mark.asyncio
async def test_writer_produces_article():
    agent = WriterAgent()
    result = await agent.run(
        project_context={"writing_style": "technical"},
        outline={
            "title": "AI Guide for Beginners",
            "outline": ["Introduction", "What are AI Agents", "How They Work", "Getting Started", "Conclusion"]
        },
        platform="公众号",
        rag_context=["AI agents are autonomous software systems - doc1"],
        word_count=500
    )
    assert "title" in result
    assert "sections" in result
    assert len(result["sections"]) >= 2
    for s in result["sections"]:
        assert "heading" in s
        assert "content" in s


@pytest.mark.asyncio
async def test_writer_respects_outline():
    agent = WriterAgent()
    outline = {
        "title": "Short Post",
        "outline": ["Brief intro", "Main point"]
    }
    result = await agent.run(
        project_context={"writing_style": "casual"},
        outline=outline,
        platform="小红书",
        rag_context=[],
        word_count=100
    )
    # Should have one section per outline item
    assert len(result["sections"]) == len(outline["outline"])


@pytest.mark.asyncio
async def test_writer_incorporates_rag_context():
    agent = WriterAgent()
    rag_context = ["Use simple language and short sentences - style_guide_1"]
    result = await agent.run(
        project_context={"writing_style": "simple"},
        outline={"title": "Test", "outline": ["Section 1"]},
        platform="公众号",
        rag_context=rag_context,
        word_count=200
    )
    assert len(result["sections"]) > 0
