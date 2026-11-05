from __future__ import annotations

import logging
import uuid
from typing import Any, Optional

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qmodels

from llm.embeddings import EmbeddingProvider, LocalEmbeddingProvider

logger = logging.getLogger(__name__)


class VectorStore:
    """Qdrant-backed vector memory for RAG retrieval."""

    def __init__(
        self,
        qdrant_url: str,
        embedding_provider: Optional[EmbeddingProvider] = None,
        collection_name: str = "fashion_knowledge",
        api_key: str = "",
    ) -> None:
        self.qdrant_url = qdrant_url
        self.api_key = api_key
        self.embedding_provider = embedding_provider or LocalEmbeddingProvider()
        self.collection_name = collection_name
        self._client: Optional[AsyncQdrantClient] = None
        self._vector_size: Optional[int] = None

    @property
    def client(self) -> AsyncQdrantClient:
        if self._client is None:
            kwargs: dict[str, Any] = {"url": self.qdrant_url, "prefer_grpc": False}
            if self.api_key:
                kwargs["api_key"] = self.api_key
            self._client = AsyncQdrantClient(**kwargs)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()
            self._client = None

    async def _collection_exists(self) -> bool:
        collections = await self.client.get_collections()
        return any(col.name == self.collection_name for col in collections.collections)

    async def _ensure_collection(self, vector_size: int) -> None:
        exists = await self._collection_exists()
        if not exists:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(
                    size=vector_size,
                    distance=qmodels.Distance.COSINE,
                ),
            )
            self._vector_size = vector_size
            logger.info(
                "Created Qdrant collection '%s' (dim=%s, cosine)",
                self.collection_name,
                vector_size,
            )
            return

        info = await self.client.get_collection(self.collection_name)
        current_size = self._extract_vector_size(info)
        self._vector_size = current_size
        if current_size != vector_size:
            logger.warning(
                "Embedding dimension mismatch in Qdrant (%s -> %s). Recreating collection...",
                current_size,
                vector_size,
            )
            await self.client.delete_collection(self.collection_name)
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(
                    size=vector_size,
                    distance=qmodels.Distance.COSINE,
                ),
            )
            self._vector_size = vector_size

    @staticmethod
    def _extract_vector_size(info: Any) -> int:
        vectors = info.config.params.vectors
        if isinstance(vectors, dict):
            first = next(iter(vectors.values()))
            return int(first.size)
        return int(vectors.size)

    @staticmethod
    def _point_id(doc_id: str) -> str:
        """Qdrant accepts UUID or unsigned int; map arbitrary string ids to UUIDv5."""
        try:
            return str(uuid.UUID(doc_id))
        except ValueError:
            return str(uuid.uuid5(uuid.NAMESPACE_URL, doc_id))

    async def upsert(self, documents: list[dict[str, Any]]) -> int:
        if not documents:
            return 0
        texts = [doc["text"] for doc in documents]
        embeddings = await self.embedding_provider.embed(texts)
        if not embeddings:
            return 0
        await self._ensure_collection(len(embeddings[0]))

        points: list[qmodels.PointStruct] = []
        for doc, vector in zip(documents, embeddings):
            payload = {
                "text": doc["text"],
                "doc_id": doc["id"],
                **(doc.get("metadata") or {}),
            }
            points.append(
                qmodels.PointStruct(
                    id=self._point_id(str(doc["id"])),
                    vector=vector,
                    payload=payload,
                )
            )

        await self.client.upsert(collection_name=self.collection_name, points=points, wait=True)
        return len(points)

    async def query(self, query: str, n_results: int = 5) -> list[dict[str, Any]]:
        if not await self._collection_exists():
            return []

        info = await self.client.get_collection(self.collection_name)
        points_count = info.points_count or 0
        if points_count == 0:
            return []

        embeddings = await self.embedding_provider.embed([query])
        query_vector = embeddings[0]
        expected = self._extract_vector_size(info)
        if len(query_vector) != expected:
            logger.warning(
                "Query embedding dim %s != collection dim %s. Returning empty.",
                len(query_vector),
                expected,
            )
            return []

        hits = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=min(n_results, points_count),
            with_payload=True,
        )

        docs: list[dict[str, Any]] = []
        for hit in hits:
            payload = dict(hit.payload or {})
            text = payload.pop("text", "")
            payload.pop("doc_id", None)
            # Qdrant cosine score is similarity (higher=better); convert to distance-like value.
            score = float(hit.score) if hit.score is not None else None
            distance = (1.0 - score) if score is not None else None
            docs.append({"text": text, "metadata": payload, "distance": distance, "score": score})
        return docs


_vector_store: Optional[VectorStore] = None


def get_vector_store(
    qdrant_url: Optional[str] = None,
    embedding_provider: Optional[EmbeddingProvider] = None,
    collection_name: str = "fashion_knowledge",
    api_key: str = "",
) -> VectorStore:
    global _vector_store
    if _vector_store is None:
        if not qdrant_url:
            raise RuntimeError("VectorStore is not initialized")
        _vector_store = VectorStore(
            qdrant_url=qdrant_url,
            embedding_provider=embedding_provider,
            collection_name=collection_name,
            api_key=api_key,
        )
    return _vector_store


def init_vector_store(
    qdrant_url: str,
    embedding_provider: EmbeddingProvider,
    collection_name: str = "fashion_knowledge",
    api_key: str = "",
) -> VectorStore:
    global _vector_store
    _vector_store = VectorStore(
        qdrant_url=qdrant_url,
        embedding_provider=embedding_provider,
        collection_name=collection_name,
        api_key=api_key,
    )
    return _vector_store
