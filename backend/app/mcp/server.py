"""MCP Server — exposes tools via Model Context Protocol"""

import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent

from app.mcp.tools import (
    rag_search,
    web_search,
    unsplash_search,
    document_index,
    export_article,
    feedback_record,
)


def create_mcp_server() -> Server:
    """Create and configure the ContentForge MCP server with registered tools."""
    server = Server("contentforge")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="rag_search",
                description="Search RAG knowledge base",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string"},
                        "query": {"type": "string"},
                        "top_k": {"type": "integer", "default": 5},
                    },
                    "required": ["project_id", "query"],
                },
            ),
            Tool(
                name="web_search",
                description="Search the web",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "num_results": {"type": "integer", "default": 5},
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="unsplash_search",
                description="Search Unsplash images",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "count": {"type": "integer", "default": 3},
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="document_index",
                description="Index documents",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string"},
                        "file_paths": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["project_id", "file_paths"],
                },
            ),
            Tool(
                name="export_article",
                description="Export article",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "article_id": {"type": "string"},
                        "format": {"type": "string"},
                        "include_review_notes": {"type": "boolean", "default": False},
                    },
                    "required": ["article_id", "format"],
                },
            ),
            Tool(
                name="feedback_record",
                description="Record feedback",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "article_id": {"type": "string"},
                        "rating": {"type": "integer"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["article_id", "rating"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "rag_search":
            result = rag_search(**arguments)
        elif name == "web_search":
            result = web_search(**arguments)
        elif name == "unsplash_search":
            result = unsplash_search(**arguments)
        elif name == "document_index":
            result = document_index(**arguments)
        elif name == "export_article":
            result = export_article(**arguments)
        elif name == "feedback_record":
            result = feedback_record(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
        return [TextContent(type="text", text=str(result))]

    return server
