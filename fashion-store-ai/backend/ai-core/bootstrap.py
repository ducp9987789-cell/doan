from __future__ import annotations

from typing import Any, Optional

from agents.shopping_agent import ShoppingAgent
from llm.embeddings import get_embedding_provider
from llm.factory import get_llm_provider
from memory.vector_store import VectorStore, init_vector_store
from tool.knowledge_indexer import KnowledgeIndexerTool
from tool.knowledge_retriever import KnowledgeRetrieverTool
from tool.product_search import ProductSearchTool

_agent: Optional[ShoppingAgent] = None
_indexer: Optional[KnowledgeIndexerTool] = None
_vector_store: Optional[VectorStore] = None


def bootstrap_ai_core(
    *,
    chroma_persist_dir: str,
    llm_provider: str,
    openai_api_key: str = "",
    openai_model: str = "gpt-4o-mini",
    openai_embedding_model: str = "text-embedding-3-small",
    gemini_api_key: str = "",
    gemini_model: str = "gemini-1.5-flash",
    db_getter: Any,
    document_loader: Any,
) -> ShoppingAgent:
    """Initialize AI-core components used by the FastAPI app."""
    global _agent, _indexer, _vector_store

    embeddings = get_embedding_provider(
        provider=llm_provider,
        openai_api_key=openai_api_key,
        openai_embedding_model=openai_embedding_model,
        gemini_api_key=gemini_api_key,
    )
    _vector_store = init_vector_store(chroma_persist_dir, embeddings)
    llm = get_llm_provider(
        provider=llm_provider,
        openai_api_key=openai_api_key,
        openai_model=openai_model,
        gemini_api_key=gemini_api_key,
        gemini_model=gemini_model,
    )
    retriever = KnowledgeRetrieverTool(_vector_store)
    product_search = ProductSearchTool(db_getter)
    _indexer = KnowledgeIndexerTool(_vector_store, document_loader)
    _agent = ShoppingAgent(llm=llm, retriever=retriever, product_search=product_search)
    return _agent


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
