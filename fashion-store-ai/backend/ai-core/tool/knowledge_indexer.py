from __future__ import annotations

from typing import Any, Callable, Awaitable

from memory.vector_store import VectorStore
from tool.base import Tool

DocumentLoader = Callable[[], Awaitable[list[dict[str, Any]]]]


class KnowledgeIndexerTool(Tool):
    name = "knowledge_indexer"
    description = "Build and upsert product/FAQ/policy documents into vector memory."

    def __init__(self, vector_store: VectorStore, document_loader: DocumentLoader) -> None:
        self.vector_store = vector_store
        self.document_loader = document_loader

    async def run(self, **_: Any) -> int:
        documents = await self.document_loader()
        return await self.vector_store.upsert(documents)
