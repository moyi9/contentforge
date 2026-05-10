import os
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.rag.vector_store import ContentForgeVectorStore


class KnowledgeIndexer:
    def __init__(self, persist_dir: str, collection_name: str):
        self.store = ContentForgeVectorStore(persist_dir, collection_name)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", "。", ".", " ", ""]
        )

    def index_directory(self, directory: str, project_id: str) -> dict:
        directory = Path(directory)
        if not directory.exists():
            return {"indexed": 0, "skipped": 0, "chunks": 0, "error": "Directory not found"}

        # Delete existing docs for this project
        self.store.delete_by_project(project_id)

        indexed = 0
        skipped = 0
        total_chunks = 0

        for filepath in directory.rglob("*"):
            if not filepath.is_file():
                continue
            if filepath.suffix.lower() not in (".md", ".markdown"):
                skipped += 1
                continue

            try:
                content = filepath.read_text(encoding="utf-8")
                chunks = self.splitter.split_text(content)

                metadatas = [{
                    "project_id": project_id,
                    "doc_type": self._guess_doc_type(filepath),
                    "source": str(filepath.relative_to(directory)),
                    "chunk_index": i
                } for i in range(len(chunks))]

                self.store.add_texts(chunks, metadatas)
                indexed += 1
                total_chunks += len(chunks)
            except Exception:
                skipped += 1

        return {"indexed": indexed, "skipped": skipped, "chunks": total_chunks}

    def _guess_doc_type(self, filepath: Path) -> str:
        name = filepath.stem.lower()
        for dtype in ["style_guide", "reference", "rule", "template", "past_work"]:
            if dtype.replace("_", "") in name.replace("_", "").replace("-", ""):
                return dtype
        return "reference"
