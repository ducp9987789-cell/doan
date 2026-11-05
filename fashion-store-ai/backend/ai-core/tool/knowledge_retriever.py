from __future__ import annotations

from typing import Any, Optional

from memory.redis_memory import RedisRAGCache
from memory.vector_store import VectorStore
from tool.base import Tool


class KnowledgeRetrieverTool(Tool):
    name = "knowledge_retriever"
    description = "Retrieve store knowledge snippets from the vector database (Qdrant), with Redis cache."

    def __init__(
        self,
        vector_store: VectorStore,
        rag_cache: Optional[RedisRAGCache] = None,
    ) -> None:
        self.vector_store = vector_store
        self.rag_cache = rag_cache

    async def run(self, query: str, n_results: int = 5, **_: Any) -> list[dict[str, Any]]:
        if self.rag_cache is not None:
            cached = await self.rag_cache.get(query, n_results)
            if cached is not None:
                return cached

        contexts = await self.vector_store.query(query, n_results=n_results)

        if self.rag_cache is not None and contexts:
            await self.rag_cache.set(query, n_results, contexts)
        return contexts
