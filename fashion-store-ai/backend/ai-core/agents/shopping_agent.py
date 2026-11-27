from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

from agents.base import AgentResult, BaseAgent
from llm.base import LLMProvider
from memory.chat_memory import ChatMemory
from memory.redis_memory import RedisChatSessionStore
from prompts.shopping import (
    NO_TOOLS_DECISION,
    ComplexityMode,
    ToolDecision,
    build_shopping_prompt,
    detect_message_complexity,
    detect_tool_mode,
    fallback_answer,
    get_system_prompt,
    simple_fallback_answer,
)
from tool.mcp import FashionMcpServer
from tool.rag import KnowledgeRetrieverTool

logger = logging.getLogger(__name__)


class ShoppingAgent(BaseAgent):
    """Shopping assistant: SIMPLE chat | COMPLEX → RAG/MCP + Redis sessions."""

    name = "shopping_agent"

    def __init__(
        self,
        llm: LLMProvider,
        retriever: KnowledgeRetrieverTool,
        mcp: FashionMcpServer,
        session_store: Optional[RedisChatSessionStore] = None,
        # Backward-compatible alias used by older tests/call sites
        product_search: Any = None,
    ) -> None:
        self.llm = llm
        self.retriever = retriever
        self.mcp = mcp
        self.session_store = session_store or RedisChatSessionStore()
        self.product_search = getattr(mcp, "product_search", None) or product_search

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

        # 1) SIMPLE vs COMPLEX (simple_mode_detection_prompt + rules)
        complexity = await detect_message_complexity(message, llm=self.llm)

        if complexity == ComplexityMode.SIMPLE:
            decision = NO_TOOLS_DECISION
            answer = simple_fallback_answer(message)
            memory.add_system(
                f"complexity=simple; tool_mode=none; reason={decision.reason}",
                event="tools",
                metadata={"complexity": "simple", "tool_mode": "none"},
            )
            memory.add_assistant(answer)
            await self.session_store.save(memory)
            return AgentResult(
                answer=answer,
                sources=[],
                suggested_products=[],
                metadata={
                    "session_id": session_key,
                    "complexity": "simple",
                    "tool_mode": "none",
                    "use_rag": False,
                    "use_mcp": False,
                    "tool_reason": decision.reason,
                    "context_count": 0,
                    "prompt_kind": "simple_fallback",
                    "mcp_tools": [t["name"] for t in self.mcp.list_tools()],
                    "memory": {
                        "working": len(memory.working),
                        "episodic": len(memory.episodic),
                        "semantic": len(memory.semantic),
                        "long_term": len(memory.long_term),
                        "system": len(memory.system),
                    },
                    "vector_backend": "qdrant",
                    "session_backend": "redis" if self.session_store.redis is not None else "memory",
                },
            )

        # COMPLEX → chọn RAG / MCP / BOTH
        decision = detect_tool_mode(message)
        rag_contexts, suggested, mcp_contexts = await self._run_tools(message, decision)

        memory.add_system(
            (
                f"complexity={complexity.value}; tool_mode={decision.mode.value}; "
                f"rag={len(rag_contexts)}; mcp_ctx={len(mcp_contexts)}; "
                f"mcp_products={len(suggested)}; reason={decision.reason}"
            ),
            event="tools",
            metadata={
                "complexity": complexity.value,
                "tool_mode": decision.mode.value,
                "use_rag": decision.use_rag,
                "use_mcp": decision.use_mcp,
                "reason": decision.reason,
                "mcp_tools": [t["name"] for t in self.mcp.list_tools()],
            },
        )

        history_text = memory.as_prompt_context(message)
        prompt = build_shopping_prompt(
            message,
            rag_contexts,
            history_text=history_text,
            role=role,
            suggested_products=suggested,
            tool_mode=decision.mode,
            mcp_contexts=mcp_contexts,
        )
        system_prompt = get_system_prompt(role)

        try:
            answer = await self.llm.generate(prompt, system=system_prompt, temperature=0.4)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM generation failed: %s", exc)
            memory.add_system(str(exc), event="llm_error")
            answer = ""

        all_contexts = list(rag_contexts) + list(mcp_contexts)
        if not answer.strip():
            answer = fallback_answer(message, all_contexts)

        memory.add_assistant(answer)
        await self.session_store.save(memory)

        sources = [
            {
                "text": ctx.get("text", "")[:300],
                "metadata": ctx.get("metadata") or {},
                "distance": ctx.get("distance"),
            }
            for ctx in all_contexts
        ]
        return AgentResult(
            answer=answer,
            sources=sources,
            suggested_products=suggested,
            metadata={
                "session_id": session_key,
                "complexity": complexity.value,
                "tool_mode": decision.mode.value,
                "use_rag": decision.use_rag,
                "use_mcp": decision.use_mcp,
                "tool_reason": decision.reason,
                "context_count": len(all_contexts),
                "prompt_kind": decision.mode.value,
                "mcp_tools": [t["name"] for t in self.mcp.list_tools()],
                "memory": {
                    "working": len(memory.working),
                    "episodic": len(memory.episodic),
                    "semantic": len(memory.semantic),
                    "long_term": len(memory.long_term),
                    "system": len(memory.system),
                },
                "vector_backend": "qdrant",
                "session_backend": "redis" if self.session_store.redis is not None else "memory",
            },
        )

    async def _run_tools(
        self,
        message: str,
        decision: ToolDecision,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
        """Chạy đúng tool theo quyết định: RAG / MCP / cả hai."""
        if decision.mode.value == "none":
            return [], [], []

        rag_task = (
            self.retriever.run(query=message, n_results=5)
            if decision.use_rag
            else asyncio.sleep(0, result=[])
        )
        product_task = (
            self.mcp.search_products(message, limit=3)
            if decision.use_mcp_products
            else asyncio.sleep(0, result=[])
        )
        mcp_extra_task = (
            self._run_mcp_extra(message, decision)
            if decision.use_mcp
            and (decision.use_mcp_store or decision.use_mcp_promo or decision.use_mcp_faq)
            else asyncio.sleep(0, result=[])
        )

        rag_contexts, suggested, mcp_contexts = await asyncio.gather(
            rag_task,
            product_task,
            mcp_extra_task,
        )
        return list(rag_contexts), list(suggested), list(mcp_contexts)

    async def _run_mcp_extra(
        self,
        message: str,
        decision: ToolDecision,
    ) -> list[dict[str, Any]]:
        """Gọi MCP store/promo/faq theo flag trong ToolDecision."""
        extra: list[dict[str, Any]] = []
        try:
            if decision.use_mcp_promo:
                promos = await self.mcp.lookup_promotions(message, limit=5)
                for promo in promos:
                    extra.append(
                        {
                            "text": (
                                f"Promotion {promo.get('code')}: {promo.get('title')}. "
                                f"{promo.get('description', '')}. "
                                f"Discount: {promo.get('discount_value')} ({promo.get('discount_type')})."
                            ),
                            "metadata": {"type": "mcp_promotion", "source": "mcp"},
                            "distance": None,
                        }
                    )

            if decision.use_mcp_store:
                store = await self.mcp.get_store_info()
                if store:
                    extra.append(
                        {
                            "text": (
                                f"Store: {store.get('store_name')}. Hotline: {store.get('hotline')}. "
                                f"Address: {store.get('address')}. "
                                f"Shipping: {store.get('shipping_policy')}. "
                                f"Return: {store.get('return_policy')}."
                            ),
                            "metadata": {"type": "mcp_store_info", "source": "mcp"},
                            "distance": None,
                        }
                    )

            if decision.use_mcp_faq:
                faqs = await self.mcp.lookup_faqs(message, limit=3)
                for faq in faqs:
                    extra.append(
                        {
                            "text": f"FAQ: Q: {faq.get('question')} A: {faq.get('answer')}",
                            "metadata": {"type": "mcp_faq", "source": "mcp"},
                            "distance": None,
                        }
                    )
        except Exception as exc:  # noqa: BLE001
            logger.warning("MCP extra tools failed: %s", exc)

        return extra
