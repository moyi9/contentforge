import chromadb
from chromadb.utils import embedding_functions


class ContentForgeVectorStore:
    def __init__(self, persist_dir: str, collection_name: str):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.ef
        )

    def add_texts(self, texts: list[str], metadatas: list[dict]) -> list[str]:
        ids = [f"doc_{self.collection.count() + i}" for i in range(len(texts))]
        self.collection.add(documents=texts, metadatas=metadatas, ids=ids)
        return ids

    def search(self, query: str, project_id: str, top_k: int = 5) -> list[dict]:
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"project_id": project_id}
        )
        return [
            {"text": doc, "metadata": meta, "distance": dist}
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]

    def delete_by_project(self, project_id: str):
        self.collection.delete(where={"project_id": project_id})
