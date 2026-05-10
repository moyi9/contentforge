"""Exporter Agent — exports articles in multiple formats"""
import os
from pathlib import Path


class ExporterAgent:
    """Exports articles to format files. Supports markdown, plain text,
    rich text (HTML), and PDF (placeholder)."""

    VALID_FORMATS = {"markdown", "plain_text", "rich_text", "pdf"}

    def __init__(self, output_dir: str = "./data/exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.name = "exporter"

    async def run(self, article: dict, format: str,
                  include_review_notes: bool = False,
                  include_image_suggestions: bool = False) -> dict:
        if format not in self.VALID_FORMATS:
            raise ValueError(
                f"Invalid format: {format}. Supported: {sorted(self.VALID_FORMATS)}"
            )

        title = article.get("title", "untitled")
        safe_filename = "".join(c if c.isalnum() or c in "-_" else "_" for c in title)

        if format == "markdown":
            content = self._to_markdown(article, include_review_notes)
            ext = ".md"
        elif format == "plain_text":
            content = self._to_plain_text(article)
            ext = ".txt"
        elif format == "rich_text":
            content = self._to_rich_text(article, include_review_notes)
            ext = ".html"
        elif format == "pdf":
            content = self._to_markdown(article, include_review_notes)
            ext = ".md"  # placeholder for pdf
        else:
            raise ValueError(f"Unknown format: {format}")

        filepath = self.output_dir / f"{safe_filename}{ext}"
        filepath.write_text(content, encoding="utf-8")

        return {
            "format": format,
            "file_path": str(filepath),
            "title": title
        }

    def _to_markdown(self, article: dict, include_review: bool) -> str:
        lines = [f"# {article.get('title', 'Untitled')}", ""]
        for section in article.get("sections", []):
            lines.append(f"## {section.get('heading', '')}")
            lines.append("")
            lines.append(section.get("content", ""))
            lines.append("")
        return "\n".join(lines)

    def _to_plain_text(self, article: dict) -> str:
        lines = [article.get("title", "Untitled"), "=" * len(article.get("title", "")), ""]
        for section in article.get("sections", []):
            lines.append(section.get("heading", ""))
            lines.append("-" * len(section.get("heading", "")))
            lines.append(section.get("content", ""))
            lines.append("")
        return "\n".join(lines)

    def _to_rich_text(self, article: dict, include_review: bool) -> str:
        title = article.get("title", "Untitled")
        html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{title}</title></head>
<body>
<h1>{title}</h1>
"""
        for section in article.get("sections", []):
            html += f"<h2>{section.get('heading', '')}</h2>\n"
            html += f"<p>{section.get('content', '')}</p>\n"
        html += "</body>\n</html>"
        return html
