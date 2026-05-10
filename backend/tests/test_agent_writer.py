"""Tests for WriterAgent with mock LLM."""

import pytest
from app.agents.writer import WriterAgent
from tests.conftest import MockLLMClient


MOCK_WRITER_RESPONSE = {
    "sections": [
        {"heading": "Introduction", "content": "This is the introduction section with substantial content to test the writer agent's ability to generate detailed text."},
        {"heading": "Core Concepts", "content": "This section covers the fundamental concepts that are essential for understanding the topic."},
        {"heading": "Implementation", "content": "Here we walk through the practical implementation steps with code examples and best practices."},
    ],
}


@pytest.mark.asyncio
async def test_writer_produces_article():
    mock_llm = MockLLMClient()
    mock_llm.set_response(MOCK_WRITER_RESPONSE)
    agent = WriterAgent(llm_client=mock_llm)

    result = await agent.run(
        project_context={},
        outline={"title": "Test Article", "outline": ["Introduction", "Core Concepts", "Implementation"]},
        platform="技术博客",
        rag_context=[],
        word_count=1000,
    )
    assert "sections" in result
    assert len(result["sections"]) == 3
    assert result["sections"][0]["heading"] == "Introduction"


@pytest.mark.asyncio
async def test_writer_respects_outline():
    mock_llm = MockLLMClient()
    mock_llm.set_response(MOCK_WRITER_RESPONSE)
    agent = WriterAgent(llm_client=mock_llm)

    outline = {"title": "AI Guide", "outline": ["Intro", "Body", "Conclusion"]}
    result = await agent.run(
        project_context={},
        outline=outline,
        platform="公众号",
        rag_context=[],
        word_count=800,
    )
    assert result["title"] == "AI Guide"
    assert len(result["sections"]) == 3


@pytest.mark.asyncio
async def test_writer_incorporates_rag_context():
    mock_llm = MockLLMClient()
    mock_llm.set_response(MOCK_WRITER_RESPONSE)
    agent = WriterAgent(llm_client=mock_llm)

    rag = ["Keep it technical and concise. Use code examples. Avoid marketing fluff."]
    result = await agent.run(
        project_context={"writing_style": "technical"},
        outline={"title": "Tutorial", "outline": ["Setup", "Code"]},
        platform="技术博客",
        rag_context=rag,
        word_count=500,
    )
    # RAG ref should be attached
    assert any(s.get("rag_ref") for s in result["sections"])
