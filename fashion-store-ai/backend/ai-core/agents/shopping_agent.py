from __future__ import annotations

import logging
from typing import Optional

from agents.base import AgentResult, BaseAgent
from llm.base import LLMProvider
from memory.chat_memory import ChatMemory
from prompts.shopping import SYSTEM_PROMPT, build_shopping_prompt, fallback_answer
from tool.knowledge_retriever import KnowledgeRetrieverTool
from tool.product_search import ProductSearchTool

logger = logging.getLogger(__name__)


class ShoppingAgent(BaseAgent):
    """RAG shopping assistant agent."""

    name = "shopping_agent"

    def __init__(
        self,
        llm: LLMProvider,
        retriever: KnowledgeRetrieverTool,
        product_search: ProductSearchTool,
    ) -> None:
        self.llm = llm
        self.retriever = retriever
        self.product_search = product_search
        self._sessions: dict[str, ChatMemory] = {}

    def _memory(self, session_id: str) -> ChatMemory:
        if session_id not in self._sessions:
            self._sessions[session_id] = ChatMemory(session_id=session_id)
        return self._sessions[session_id]

    async def run(self, message: str, *, session_id: Optional[str] = None) -> AgentResult:
        session_key = session_id or "anonymous"
        memory = self._memory(session_key)
        memory.add_user(message)

        contexts = await self.retriever.run(query=message, n_results=5)
        prompt = build_shopping_prompt(message, contexts, history_text=memory.as_text())
        try:
            answer = await self.llm.generate(prompt, system=SYSTEM_PROMPT, temperature=0.4)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM generation failed: %s", exc)
            answer = ""

        if not answer.strip():
            answer = fallback_answer(message, contexts)

        suggested = await self.product_search.run(query=message, limit=3)
        memory.add_assistant(answer)

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
            metadata={"session_id": session_key, "context_count": len(contexts)},
        )
