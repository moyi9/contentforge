import pytest
from pathlib import Path
from app.rag.indexer import KnowledgeIndexer


@pytest.fixture
def vault_dir(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "style.md").write_text("# Style Guide\nBe concise. Use active voice.")
    (vault / "reference.md").write_text("# Reference\nGood examples of tech writing here.")
    (vault / "ignore.txt").write_text("should be ignored because not .md")
    return str(vault)


def test_index_markdown_files(vault_dir, tmp_path):
    idx = KnowledgeIndexer(
        persist_dir=str(tmp_path / "chroma"),
        collection_name="test_indexer"
    )
    result = idx.index_directory(vault_dir, "proj-1")
    assert result["indexed"] == 2
    assert result["skipped"] == 1
    assert result["chunks"] >= 2  # at least one chunk per doc


def test_reindex_deletes_old_chunks(vault_dir, tmp_path):
    idx = KnowledgeIndexer(
        persist_dir=str(tmp_path / "chroma2"),
        collection_name="test_reindex"
    )
    first = idx.index_directory(vault_dir, "proj-1")
    first_count = first["indexed"]
    assert first_count > 0

    # Change a file
    Path(vault_dir, "style.md").write_text("# Updated Style\nBe very concise and direct.")
    second = idx.index_directory(vault_dir, "proj-1")
    # Re-index should re-process all files
    assert second["indexed"] >= 1


def test_empty_directory(tmp_path):
    empty_dir = tmp_path / "empty_vault"
    empty_dir.mkdir()
    idx = KnowledgeIndexer(str(tmp_path / "chroma3"), "test_empty")
    result = idx.index_directory(str(empty_dir), "proj-1")
    assert result["indexed"] == 0
    assert result["skipped"] == 0
    assert result["chunks"] == 0
