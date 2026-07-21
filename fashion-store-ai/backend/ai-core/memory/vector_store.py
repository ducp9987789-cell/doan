from __future__ import annotations

import logging
from typing import Any, Optional

import chromadb
from chromadb.api.models.Collection import Collection

from llm.embeddings import EmbeddingProvider, LocalEmbeddingProvider

logger = logging.getLogger(__name__)


class VectorStore:
    """Chroma-backed vector memory for RAG retrieval."""

    def __init__(
        self,
        persist_dir: str,
        embedding_provider: Optional[EmbeddingProvider] = None,
        collection_name: str = "fashion_knowledge",
    ) -> None:
        self.persist_dir = persist_dir
        self.embedding_provider = embedding_provider or LocalEmbeddingProvider()
        self.collection_name = collection_name
        self._client: Optional[chromadb.PersistentClient] = None
        self._collection: Optional[Collection] = None

    @property
    def client(self) -> chromadb.PersistentClient:
        if self._client is None:
            self._client = chromadb.PersistentClient(path=self.persist_dir)
        return self._client

    @property
    def collection(self) -> Collection:
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    async def upsert(self, documents: list[dict[str, Any]]) -> int:
        if not documents:
            return 0
        ids = [doc["id"] for doc in documents]
        texts = [doc["text"] for doc in documents]
        metadatas = [doc.get("metadata") or {} for doc in documents]
        embeddings = await self.embedding_provider.embed(texts)
        self.collection.upsert(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
        return len(documents)

    async def query(self, query: str, n_results: int = 5) -> list[dict[str, Any]]:
        if self.collection.count() == 0:
            return []
        embeddings = await self.embedding_provider.embed([query])
        result = self.collection.query(
            query_embeddings=embeddings,
            n_results=min(n_results, self.collection.count()),
        )
        docs: list[dict[str, Any]] = []
        documents = result.get("documents") or [[]]
        metadatas = result.get("metadatas") or [[]]
        distances = result.get("distances") or [[]]
        for idx, text in enumerate(documents[0]):
            docs.append(
                {
                    "text": text,
                    "metadata": metadatas[0][idx] if idx < len(metadatas[0]) else {},
                    "distance": distances[0][idx] if idx < len(distances[0]) else None,
                }
            )
        return docs


_vector_store: Optional[VectorStore] = None


def get_vector_store(
    persist_dir: Optional[str] = None,
    embedding_provider: Optional[EmbeddingProvider] = None,
) -> VectorStore:
    global _vector_store
    if _vector_store is None:
        if not persist_dir:
            raise RuntimeError("VectorStore is not initialized")
        _vector_store = VectorStore(persist_dir=persist_dir, embedding_provider=embedding_provider)
    return _vector_store


def init_vector_store(persist_dir: str, embedding_provider: EmbeddingProvider) -> VectorStore:
    global _vector_store
    _vector_store = VectorStore(persist_dir=persist_dir, embedding_provider=embedding_provider)
    return _vector_store
