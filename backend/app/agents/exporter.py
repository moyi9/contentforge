"""Exporter Agent — formats articles into various output formats.

Currently uses templates for deterministic output; LLM enhancement
for richer formatting (e.g., html styling) can be added later.
"""

import json
import os
from datetime import datetime
from app.config import settings


EXPORT_DIR = os.path.join(os.path.dirname(settings.database_url.replace("sqlite:///", "")), "exports") if settings.database_url.startswith("sqlite:///") else "./data/exports"


class ExporterAgent:
    """Formats articles into Markdown, Plain Text, Rich Text (HTML), or PDF."""

    def __init__(self, output_dir: str | None = None):
        self.name = "exporter"
        self._export_dir = output_dir or EXPORT_DIR

    async def run(self, article: dict, format: str,
                  include_review_notes: bool = False,
                  include_image_suggestions: bool = True) -> dict:
        """Export an article to the requested format."""
        os.makedirs(self._export_dir, exist_ok=True)

        title = article.get("title", "Untitled")
        sections = article.get("sections", [])

        if format == "markdown":
            content = self._to_markdown(title, sections)
        elif format == "plain_text":
            content = self._to_plain_text(title, sections)
        elif format == "rich_text":
            content = self._to_rich_text(title, sections)
        elif format == "pdf":
            # PDF currently exported as markdown (real PDF conversion needs wkhtmltopdf or similar)
            content = self._to_markdown(title, sections)
        else:
            raise ValueError(f"Unsupported format: {format}")

        filename = f"{title.replace(' ', '_')[:40]}.{self._extension(format)}"
        filepath = os.path.join(self._export_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "format": format,
            "file_path": filepath,
            "content": content[:500] + "..." if len(content) > 500 else content,
        }

    def _to_markdown(self, title: str, sections: list) -> str:
        lines = [f"# {title}\n"]
        for sec in sections:
            lines.append(f"\n## {sec.get('heading', '')}\n")
            lines.append(f"{sec.get('content', '')}\n")
        return "".join(lines)

    def _to_plain_text(self, title: str, sections: list) -> str:
        lines = [f"{title}\n{'=' * len(title)}\n"]
        for sec in sections:
            lines.append(f"\n{sec.get('heading', '')}\n{'-' * len(sec.get('heading', ''))}\n")
            lines.append(f"{sec.get('content', '')}\n")
        return "".join(lines)

    def _to_rich_text(self, title: str, sections: list) -> str:
        """Basic HTML export."""
        parts = ["<!DOCTYPE html><html><head><meta charset='utf-8'>",
                 f"<title>{title}</title>",
                 "<style>body{max-width:800px;margin:auto;padding:2em;font-family:system-ui,sans-serif;"
                 "line-height:1.8}h1{color:#333}h2{color:#555}p{color:#444}</style></head><body>",
                 f"<h1>{title}</h1>"]
        for sec in sections:
            parts.append(f"<h2>{sec.get('heading', '')}</h2>")
            parts.append(f"<p>{sec.get('content', '')}</p>")
        parts.append("</body></html>")
        return "\n".join(parts)

    def _extension(self, fmt: str) -> str:
        return {"markdown": "md", "plain_text": "txt", "rich_text": "html", "pdf": "md"}.get(fmt, "txt")
