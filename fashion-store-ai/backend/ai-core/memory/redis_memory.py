from __future__ import annotations

import json
import logging
from typing import Any, Optional

from memory.chat_memory import ChatMemory, ChatTurn

logger = logging.getLogger(__name__)


class RedisChatSessionStore:
    """Persist chat turns in Redis with TTL; fall back to in-process memory."""

    KEY_PREFIX = "chat:session:"

    def __init__(
        self,
        redis_client: Any = None,
        ttl_seconds: int = 86400,
    ) -> None:
        self.redis = redis_client
        self.ttl_seconds = ttl_seconds
        self._local: dict[str, ChatMemory] = {}

    def _key(self, session_id: str) -> str:
        return f"{self.KEY_PREFIX}{session_id}"

    async def get(self, session_id: str) -> ChatMemory:
        if self.redis is not None:
            try:
                raw = await self.redis.get(self._key(session_id))
                if raw:
                    data = json.loads(raw)
                    turns = [ChatTurn(role=t["role"], content=t["content"]) for t in data.get("turns", [])]
                    return ChatMemory(
                        session_id=session_id,
                        turns=turns,
                        metadata=data.get("metadata") or {},
                    )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Redis session read failed (%s); using memory fallback.", exc)

        if session_id not in self._local:
            self._local[session_id] = ChatMemory(session_id=session_id)
        return self._local[session_id]

    async def save(self, memory: ChatMemory) -> None:
        self._local[memory.session_id] = memory
        if self.redis is None:
            return
        payload = {
            "turns": [{"role": t.role, "content": t.content} for t in memory.turns],
            "metadata": memory.metadata,
        }
        try:
            await self.redis.set(
                self._key(memory.session_id),
                json.dumps(payload, ensure_ascii=False),
                ex=self.ttl_seconds,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Redis session write failed (%s).", exc)


class RedisRAGCache:
    """Short-lived cache for RAG retrieval results."""

    KEY_PREFIX = "rag:cache:"

    def __init__(self, redis_client: Any = None, ttl_seconds: int = 300) -> None:
        self.redis = redis_client
        self.ttl_seconds = ttl_seconds

    def _key(self, query: str, n_results: int) -> str:
        import hashlib

        digest = hashlib.sha256(f"{query.strip().lower()}::{n_results}".encode("utf-8")).hexdigest()
        return f"{self.KEY_PREFIX}{digest}"

    async def get(self, query: str, n_results: int) -> Optional[list[dict[str, Any]]]:
        if self.redis is None:
            return None
        try:
            raw = await self.redis.get(self._key(query, n_results))
            if not raw:
                return None
            return json.loads(raw)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Redis RAG cache read failed (%s).", exc)
            return None

    async def set(self, query: str, n_results: int, contexts: list[dict[str, Any]]) -> None:
        if self.redis is None:
            return
        try:
            await self.redis.set(
                self._key(query, n_results),
                json.dumps(contexts, ensure_ascii=False),
                ex=self.ttl_seconds,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Redis RAG cache write failed (%s).", exc)

    async def invalidate_all(self) -> None:
        """Best-effort clear of RAG cache keys after reindex."""
        if self.redis is None:
            return
        try:
            cursor = 0
            pattern = f"{self.KEY_PREFIX}*"
            while True:
                cursor, keys = await self.redis.scan(cursor=cursor, match=pattern, count=200)
                if keys:
                    await self.redis.delete(*keys)
                if cursor == 0:
                    break
        except Exception as exc:  # noqa: BLE001
            logger.warning("Redis RAG cache invalidate failed (%s).", exc)
