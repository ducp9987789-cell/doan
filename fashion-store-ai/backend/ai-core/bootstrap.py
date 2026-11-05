from __future__ import annotations

from typing import Any, Optional

from agents.shopping_agent import ShoppingAgent
from llm.embeddings import get_embedding_provider
from llm.factory import get_llm_provider
from memory.redis_memory import RedisChatSessionStore, RedisRAGCache
from memory.vector_store import VectorStore, init_vector_store
from tool.knowledge_indexer import KnowledgeIndexerTool
from tool.knowledge_retriever import KnowledgeRetrieverTool
from tool.product_search import ProductSearchTool

_agent: Optional[ShoppingAgent] = None
_indexer: Optional[KnowledgeIndexerTool] = None
_vector_store: Optional[VectorStore] = None
_session_store: Optional[RedisChatSessionStore] = None
_rag_cache: Optional[RedisRAGCache] = None


def bootstrap_ai_core(
    *,
    qdrant_url: str,
    qdrant_collection: str = "fashion_knowledge",
    qdrant_api_key: str = "",
    llm_provider: str,
    openai_api_key: str = "",
    openai_model: str = "gpt-4o-mini",
    openai_embedding_model: str = "text-embedding-3-small",
    gemini_api_key: str = "",
    gemini_model: str = "gemini-1.5-flash",
    db_getter: Any,
    document_loader: Any,
    redis_client: Any = None,
    redis_session_ttl_seconds: int = 86400,
    redis_rag_cache_ttl_seconds: int = 300,
    # Backward-compatible unused kwargs from older callers
    chroma_persist_dir: str = "",
) -> ShoppingAgent:
    """Initialize AI-core components used by the FastAPI app."""
    global _agent, _indexer, _vector_store, _session_store, _rag_cache
    _ = chroma_persist_dir  # retained for older call sites

    embeddings = get_embedding_provider(
        provider=llm_provider,
        openai_api_key=openai_api_key,
        openai_embedding_model=openai_embedding_model,
        gemini_api_key=gemini_api_key,
    )
    _vector_store = init_vector_store(
        qdrant_url=qdrant_url,
        embedding_provider=embeddings,
        collection_name=qdrant_collection,
        api_key=qdrant_api_key,
    )
    llm = get_llm_provider(
        provider=llm_provider,
        openai_api_key=openai_api_key,
        openai_model=openai_model,
        gemini_api_key=gemini_api_key,
        gemini_model=gemini_model,
    )

    _rag_cache = RedisRAGCache(redis_client, ttl_seconds=redis_rag_cache_ttl_seconds)
    _session_store = RedisChatSessionStore(redis_client, ttl_seconds=redis_session_ttl_seconds)

    retriever = KnowledgeRetrieverTool(_vector_store, rag_cache=_rag_cache)
    product_search = ProductSearchTool(db_getter)
    _indexer = KnowledgeIndexerTool(_vector_store, document_loader, rag_cache=_rag_cache)
    _agent = ShoppingAgent(
        llm=llm,
        retriever=retriever,
        product_search=product_search,
        session_store=_session_store,
    )
    return _agent


def bind_redis(redis_client: Any) -> None:
    """Attach a live Redis client after AI-core bootstrap (async connect happens in lifespan)."""
    global _session_store, _rag_cache
    if _session_store is not None:
        _session_store.redis = redis_client
    if _rag_cache is not None:
        _rag_cache.redis = redis_client


def get_shopping_agent() -> ShoppingAgent:
    if _agent is None:
        raise RuntimeError("AI-core is not bootstrapped")
    return _agent


def get_knowledge_indexer() -> KnowledgeIndexerTool:
    if _indexer is None:
        raise RuntimeError("AI-core is not bootstrapped")
    return _indexer


def get_vector_store_instance() -> VectorStore:
    if _vector_store is None:
        raise RuntimeError("AI-core is not bootstrapped")
    return _vector_store
