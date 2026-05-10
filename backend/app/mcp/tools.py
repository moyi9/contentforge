"""MCP Tools — standardized Agent tool calls"""

from typing import Optional


def rag_search(project_id: str, query: str, top_k: int = 5) -> dict:
    """Search the RAG knowledge base for relevant documents."""
    # Stub: real implementation plugs into ContentForgeVectorStore
    return {"results": [], "project_id": project_id, "query": query}


def web_search(query: str, num_results: int = 5) -> dict:
    """Search the web for current information."""
    return {"results": [], "query": query}


def unsplash_search(query: str, count: int = 3) -> dict:
    """Search Unsplash for relevant images."""
    return {"results": [], "query": query}


def document_index(project_id: str, file_paths: list[str]) -> dict:
    """Index documents into the knowledge base."""
    return {"status": "ok", "indexed": 0, "project_id": project_id}


def export_article(
    article_id: str,
    format: str,
    include_review_notes: bool = False,
    include_image_suggestions: bool = True,
) -> dict:
    """Export article in specified format."""
    VALID_FORMATS = {"pdf", "markdown", "rich_text", "plain_text"}
    if format not in VALID_FORMATS:
        raise ValueError(f"Invalid format: {format}. Supported: {VALID_FORMATS}")
    return {"status": "ok", "article_id": article_id, "format": format}


def feedback_record(article_id: str, rating: int, tags: list[str]) -> dict:
    """Record user feedback on generated content."""
    return {"status": "recorded", "article_id": article_id, "rating": rating, "tags": tags}
