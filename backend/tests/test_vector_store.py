import pytest
from app.rag.vector_store import ContentForgeVectorStore


def test_add_and_search(tmp_path):
    store = ContentForgeVectorStore(
        persist_dir=str(tmp_path / "chroma"),
        collection_name="test_collection"
    )
    docs = ["AI agents are autonomous systems.", "Content creation requires creativity."]
    metadatas = [
        {"project_id": "proj-1", "doc_type": "reference", "source": "doc1.md"},
        {"project_id": "proj-1", "doc_type": "style_guide", "source": "doc2.md"}
    ]
    ids = store.add_texts(docs, metadatas)
    assert len(ids) == 2

    results = store.search("AI autonomous", project_id="proj-1", top_k=2)
    assert len(results) > 0
    assert "AI" in results[0]["text"]


def test_search_with_project_filter(tmp_path):
    store = ContentForgeVectorStore(str(tmp_path / "chroma2"), "test2")
    store.add_texts(
        ["Doc from project A"],
        [{"project_id": "proj-a", "doc_type": "reference", "source": "a.md"}]
    )
    store.add_texts(
        ["Doc from project B"],
        [{"project_id": "proj-b", "doc_type": "reference", "source": "b.md"}]
    )
    results = store.search("Doc", project_id="proj-a", top_k=5)
    assert len(results) == 1
    assert "project A" in results[0]["text"]


def test_delete_by_project(tmp_path):
    store = ContentForgeVectorStore(str(tmp_path / "chroma3"), "test3")
    store.add_texts(["Doc A"], [{"project_id": "p1", "doc_type": "x", "source": "a.md"}])
    store.delete_by_project("p1")
    results = store.search("Doc", project_id="p1", top_k=5)
    assert len(results) == 0
