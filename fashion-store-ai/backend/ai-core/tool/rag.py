"""RAG tools — truy xuất / index kho tri thức vector (Qdrant + Redis cache).

Phân biệt với MCP (`tool/mcp.py`):
- RAG: tìm ngữ cảnh theo ngữ nghĩa từ embeddings.
- MCP: gọi công cụ có cấu trúc (product search, store info, promotion,...).
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Optional

from memory.redis_memory import RedisRAGCache
from memory.vector_store import VectorStore
from tool.base import Tool

DocumentLoader = Callable[[], Awaitable[list[dict[str, Any]]]]

__all__ = [
    "DocumentLoader",
    "KnowledgeRetrieverTool",
    "KnowledgeIndexerTool",
    "build_knowledge_documents",
]


async def build_knowledge_documents(db: Any) -> list[dict[str, Any]]:
    """Load MongoDB store data into RAG documents for Qdrant indexing."""
    documents: list[dict[str, Any]] = []

    products = await db.products.find({"is_active": True}).to_list(length=1000)
    for product in products:
        text = (
            f"Product: {product['name']}. Category: {product.get('category_name', '')}. "
            f"Price: {product.get('sale_price') or product['price']} VND. "
            f"Colors: {', '.join(product.get('colors') or [])}. "
            f"Sizes: {', '.join(product.get('sizes') or [])}. "
            f"Stock: {product.get('stock', 0)}. "
            f"Description: {product.get('description', '')}. "
            f"Tags: {', '.join(product.get('tags') or [])}."
        )
        documents.append(
            {
                "id": f"product-{product['_id']}",
                "text": text,
                "metadata": {"type": "product", "product_id": str(product["_id"])},
            }
        )

    faqs = await db.faqs.find({"is_active": True}).to_list(length=500)
    for faq in faqs:
        documents.append(
            {
                "id": f"faq-{faq['_id']}",
                "text": f"FAQ ({faq.get('category', 'general')}): Q: {faq['question']} A: {faq['answer']}",
                "metadata": {"type": "faq", "faq_id": str(faq["_id"])},
            }
        )

    promotions = await db.promotions.find({"is_active": True}).to_list(length=200)
    for promo in promotions:
        documents.append(
            {
                "id": f"promo-{promo['_id']}",
                "text": (
                    f"Promotion code {promo['code']}: {promo['title']}. "
                    f"{promo.get('description', '')}. Discount: {promo['discount_value']} "
                    f"({promo.get('discount_type')}). Min order: {promo.get('min_order_value', 0)}."
                ),
                "metadata": {"type": "promotion", "code": promo["code"]},
            }
        )

    store = await db.store_info.find_one({})
    if store:
        documents.append(
            {
                "id": "store-info",
                "text": (
                    f"Store: {store.get('store_name')}. Hotline: {store.get('hotline')}. "
                    f"Email: {store.get('email')}. Address: {store.get('address')}. "
                    f"About: {store.get('about')}. Shipping policy: {store.get('shipping_policy')}. "
                    f"Return policy: {store.get('return_policy')}."
                ),
                "metadata": {"type": "store_info"},
            }
        )

    return documents


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
