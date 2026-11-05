from __future__ import annotations

from typing import Any, Awaitable, Callable, Optional

from memory.redis_memory import RedisRAGCache
from memory.vector_store import VectorStore
from tool.base import Tool

DocumentLoader = Callable[[], Awaitable[list[dict[str, Any]]]]


class KnowledgeIndexerTool(Tool):
    name = "knowledge_indexer"
    description = "Build and upsert product/FAQ/policy documents into Qdrant vector memory."

    def __init__(
        self,
        vector_store: VectorStore,
        document_loader: DocumentLoader,
        rag_cache: Optional[RedisRAGCache] = None,
    ) -> None:
        self.vector_store = vector_store
        self.document_loader = document_loader
        self.rag_cache = rag_cache

    async def run(self, **_: Any) -> int:
        documents = await self.document_loader()
        count = await self.vector_store.upsert(documents)
        if self.rag_cache is not None:
            await self.rag_cache.invalidate_all()
        return count
