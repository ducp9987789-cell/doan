from __future__ import annotations

from typing import Any

from memory.vector_store import VectorStore
from tool.base import Tool


class KnowledgeRetrieverTool(Tool):
    name = "knowledge_retriever"
    description = "Retrieve store knowledge snippets from the vector database."

    def __init__(self, vector_store: VectorStore) -> None:
        self.vector_store = vector_store

    async def run(self, query: str, n_results: int = 5, **_: Any) -> list[dict[str, Any]]:
        return await self.vector_store.query(query, n_results=n_results)
