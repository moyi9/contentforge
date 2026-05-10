"""Tests for MCP Tools — standardized Agent tool calls"""

import pytest
from app.mcp.tools import rag_search, web_search, export_article, feedback_record


def test_rag_search():
    """RAG search returns a list of results"""
    result = rag_search(project_id="test-proj", query="AI agents", top_k=3)
    assert "results" in result
    assert isinstance(result["results"], list)


def test_web_search():
    """Web search returns results"""
    result = web_search(query="AI trends 2026", num_results=5)
    assert "results" in result
    assert isinstance(result["results"], list)


def test_export_article_validates_format():
    """Export rejects invalid format"""
    with pytest.raises(ValueError):
        export_article(article_id="art-1", format="docx")


def test_feedback_record():
    """Feedback records correctly"""
    result = feedback_record(
        article_id="art-1",
        rating=4,
        tags=["good", "concise"],
    )
    assert result["status"] == "recorded"
