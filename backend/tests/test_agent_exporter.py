import pytest
from pathlib import Path
from app.agents.exporter import ExporterAgent

SAMPLE_ARTICLE = {
    "title": "Test Article",
    "sections": [
        {"heading": "Section 1", "content": "Hello world content here."},
        {"heading": "Section 2", "content": "More content for testing."}
    ]
}


@pytest.mark.asyncio
async def test_export_markdown(tmp_path):
    agent = ExporterAgent(output_dir=str(tmp_path))
    result = await agent.run(
        article=SAMPLE_ARTICLE,
        format="markdown",
        include_review_notes=False,
        include_image_suggestions=False
    )
    assert result["format"] == "markdown"
    assert "file_path" in result
    assert Path(result["file_path"]).exists()
    content = Path(result["file_path"]).read_text()
    assert "# Test Article" in content
    assert "Hello world" in content
    assert "## Section 1" in content


@pytest.mark.asyncio
async def test_export_plain_text(tmp_path):
    agent = ExporterAgent(output_dir=str(tmp_path))
    result = await agent.run(
        article=SAMPLE_ARTICLE,
        format="plain_text",
        include_review_notes=False,
        include_image_suggestions=False
    )
    assert result["format"] == "plain_text"
    content = Path(result["file_path"]).read_text()
    assert "Test Article" in content
    assert "Hello world" in content


@pytest.mark.asyncio
async def test_export_rich_text(tmp_path):
    agent = ExporterAgent(output_dir=str(tmp_path))
    result = await agent.run(
        article=SAMPLE_ARTICLE,
        format="rich_text",
        include_review_notes=False,
        include_image_suggestions=False
    )
    assert result["format"] == "rich_text"
    content = Path(result["file_path"]).read_text()
    assert "<!DOCTYPE html>" in content or "Test Article" in content


@pytest.mark.asyncio
async def test_export_invalid_format(tmp_path):
    agent = ExporterAgent(output_dir=str(tmp_path))
    with pytest.raises(ValueError, match="Invalid format"):
        await agent.run(
            article=SAMPLE_ARTICLE,
            format="docx",
            include_review_notes=False,
            include_image_suggestions=False
        )
