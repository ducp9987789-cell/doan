from __future__ import annotations

import asyncio
import logging
from typing import Optional

from agents.base import AgentResult, BaseAgent
from llm.base import LLMProvider
from memory.chat_memory import ChatMemory
from memory.redis_memory import RedisChatSessionStore
from prompts.shopping import (
    build_shopping_prompt,
    fallback_answer,
    get_system_prompt,
    is_shopping_intent,
)
from tool.knowledge_retriever import KnowledgeRetrieverTool
from tool.product_search import ProductSearchTool

logger = logging.getLogger(__name__)


class ShoppingAgent(BaseAgent):
    """RAG shopping assistant agent backed by Qdrant retrieval + Redis sessions."""

    name = "shopping_agent"

    def __init__(
        self,
        llm: LLMProvider,
        retriever: KnowledgeRetrieverTool,
        product_search: ProductSearchTool,
        session_store: Optional[RedisChatSessionStore] = None,
    ) -> None:
        self.llm = llm
        self.retriever = retriever
        self.product_search = product_search
        self.session_store = session_store or RedisChatSessionStore()

    async def run(
        self,
        message: str,
        *,
        session_id: Optional[str] = None,
        role: Optional[str] = None,
    ) -> AgentResult:
        session_key = session_id or "anonymous"
        memory: ChatMemory = await self.session_store.get(session_key)
        memory.add_user(message)

        shopping = is_shopping_intent(message)

        # Qdrant (RAG) + MongoDB (product cards) chạy song song khi có ý định mua sắm
        if shopping:
            contexts, suggested = await asyncio.gather(
                self.retriever.run(query=message, n_results=5),
                self.product_search.run(query=message, limit=3),
            )
        else:
            contexts = await self.retriever.run(query=message, n_results=5)
            suggested = []

        prompt = build_shopping_prompt(
            message,
            contexts,
            history_text=memory.as_text(),
            role=role,
            suggested_products=suggested,
        )
        system_prompt = get_system_prompt(role)

        try:
            answer = await self.llm.generate(prompt, system=system_prompt, temperature=0.4)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM generation failed: %s", exc)
            answer = ""

        if not answer.strip():
            answer = fallback_answer(message, contexts)

        memory.add_assistant(answer)
        await self.session_store.save(memory)

        sources = [
            {
                "text": ctx.get("text", "")[:300],
                "metadata": ctx.get("metadata") or {},
                "distance": ctx.get("distance"),
            }
            for ctx in contexts
        ]
        return AgentResult(
            answer=answer,
            sources=sources,
            suggested_products=suggested,
            metadata={
                "session_id": session_key,
                "context_count": len(contexts),
                "shopping_intent": shopping,
                "vector_backend": "qdrant",
                "session_backend": "redis" if self.session_store.redis is not None else "memory",
            },
        )
