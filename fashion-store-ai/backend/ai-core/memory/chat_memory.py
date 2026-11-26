from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class MemoryKind(str, Enum):
    WORKING = "working"  # hội thoại gần — LLM chỉ nhìn vài tin gần
    EPISODIC = "episodic"  # đoạn cũ hơn khi working đầy
    SEMANTIC = "semantic"  # fact đã lọc, retrieve theo độ giống
    LONG_TERM = "long_term"  # persist preference lâu dài
    SYSTEM = "system"  # log nội bộ — không đưa vào prompt user–bot


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ChatTurn:
    role: str
    content: str
    created_at: str = field(default_factory=_utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChatTurn":
        return cls(
            role=data.get("role", "user"),
            content=data.get("content", ""),
            created_at=data.get("created_at") or _utcnow(),
            metadata=data.get("metadata") or {},
        )


@dataclass
class MemoryItem:
    kind: str
    role: str
    content: str
    created_at: str = field(default_factory=_utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    keywords: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at,
            "metadata": self.metadata,
            "keywords": self.keywords,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryItem":
        return cls(
            kind=data.get("kind", MemoryKind.EPISODIC.value),
            role=data.get("role", "system"),
            content=data.get("content", ""),
            created_at=data.get("created_at") or _utcnow(),
            metadata=data.get("metadata") or {},
            keywords=list(data.get("keywords") or []),
        )


_STOPWORDS = {
    "cái",
    "này",
    "kia",
    "cho",
    "tôi",
    "mình",
    "bạn",
    "là",
    "của",
    "và",
    "với",
    "có",
    "không",
    "gì",
    "như",
    "thế",
    "nào",
    "muốn",
    "cần",
    "một",
    "các",
    "được",
    "trong",
    "khi",
    "để",
    "về",
    "hay",
    "hoặc",
    "the",
    "and",
    "for",
}


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"\w+", (text or "").lower())
        if len(token) > 1 and token not in _STOPWORDS
    }


def _similarity(a: str, b: str) -> float:
    ta, tb = _tokenize(a), _tokenize(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


@dataclass
class ChatMemory:
    """Memory đa tầng: WORKING / EPISODIC / SEMANTIC / LONG_TERM / SYSTEM."""

    session_id: str
    working: list[ChatTurn] = field(default_factory=list)
    episodic: list[MemoryItem] = field(default_factory=list)
    semantic: list[MemoryItem] = field(default_factory=list)
    long_term: list[MemoryItem] = field(default_factory=list)
    system: list[MemoryItem] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    WORKING_LIMIT: int = 20
    EPISODIC_LIMIT: int = 40
    SEMANTIC_LIMIT: int = 30
    LONG_TERM_LIMIT: int = 20
    SYSTEM_LIMIT: int = 50

    # --- backward-compat alias ---
    @property
    def turns(self) -> list[ChatTurn]:
        return self.working

    @turns.setter
    def turns(self, value: list[ChatTurn]) -> None:
        self.working = list(value)

    def add_user(self, content: str) -> None:
        self._append_working(ChatTurn(role="user", content=content))
        self._extract_and_store_facts(content)

    def add_assistant(self, content: str) -> None:
        self._append_working(ChatTurn(role="assistant", content=content))

    def add_system(
        self,
        content: str,
        *,
        event: str = "log",
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log nội bộ (tool/error/event) — không đưa vào prompt hội thoại."""
        self.system.append(
            MemoryItem(
                kind=MemoryKind.SYSTEM.value,
                role="system",
                content=content,
                metadata={"event": event, **(metadata or {})},
            )
        )
        if len(self.system) > self.SYSTEM_LIMIT:
            self.system = self.system[-self.SYSTEM_LIMIT :]

    def add_semantic_fact(
        self,
        content: str,
        *,
        keywords: Optional[list[str]] = None,
        promote_long_term: bool = False,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        item = MemoryItem(
            kind=MemoryKind.SEMANTIC.value,
            role="fact",
            content=content,
            keywords=keywords or sorted(_tokenize(content)),
            metadata=metadata or {},
        )
        self._upsert_fact(self.semantic, item, self.SEMANTIC_LIMIT)
        if promote_long_term:
            long_item = MemoryItem(
                kind=MemoryKind.LONG_TERM.value,
                role="fact",
                content=content,
                keywords=item.keywords,
                metadata={**(metadata or {}), "source": "semantic"},
            )
            self._upsert_fact(self.long_term, long_item, self.LONG_TERM_LIMIT)

    def recent(self, limit: int = 6) -> list[ChatTurn]:
        return self.working[-limit:]

    def retrieve_semantic(
        self,
        query: str,
        *,
        threshold: float = 0.12,
        limit: int = 5,
    ) -> list[MemoryItem]:
        scored = [
            (item, _similarity(query, f"{item.content} {' '.join(item.keywords)}"))
            for item in (*self.long_term, *self.semantic)
        ]
        scored = [(item, score) for item, score in scored if score >= threshold]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        seen: set[str] = set()
        results: list[MemoryItem] = []
        for item, _score in scored:
            key = item.content.strip().lower()
            if key in seen:
                continue
            seen.add(key)
            results.append(item)
            if len(results) >= limit:
                break
        return results

    def retrieve_episodic(
        self,
        query: str,
        *,
        threshold: float = 0.08,
        limit: int = 4,
    ) -> list[MemoryItem]:
        scored = [
            (item, _similarity(query, item.content))
            for item in self.episodic
        ]
        scored = [(item, score) for item, score in scored if score >= threshold]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [item for item, _ in scored[:limit]]

    def as_text(self, limit: int = 6) -> str:
        """Legacy: chỉ WORKING gần đây."""
        lines = [f"{turn.role}: {turn.content}" for turn in self.recent(limit)]
        return "\n".join(lines)

    def as_prompt_context(self, query: str = "", *, working_limit: int = 12) -> str:
        """Ghép context cho LLM theo ưu tiên tầng — không gồm SYSTEM."""
        blocks: list[str] = []

        long_term = self.long_term[-8:]
        if long_term:
            lines = [f"- {item.content}" for item in long_term]
            blocks.append("=== GHI NHỚ DÀI HẠN (LONG_TERM) ===\n" + "\n".join(lines))

        semantic = self.retrieve_semantic(query or self._last_user_text(), limit=5)
        if semantic:
            lines = [f"- {item.content}" for item in semantic]
            blocks.append("=== FACT LIÊN QUAN (SEMANTIC) ===\n" + "\n".join(lines))

        episodic = self.retrieve_episodic(query or self._last_user_text(), limit=3)
        if episodic:
            lines = [f"- {item.content}" for item in episodic]
            blocks.append("=== KỶ NIỆM CŨ (EPISODIC) ===\n" + "\n".join(lines))

        working = self.recent(working_limit)
        if working:
            lines = [f"{turn.role}: {turn.content}" for turn in working]
            blocks.append("=== HỘI THOẠI GẦN (WORKING) ===\n" + "\n".join(lines))

        return "\n\n".join(blocks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "working": [t.to_dict() for t in self.working],
            # legacy key for older readers
            "turns": [t.to_dict() for t in self.working],
            "episodic": [i.to_dict() for i in self.episodic],
            "semantic": [i.to_dict() for i in self.semantic],
            "long_term": [i.to_dict() for i in self.long_term],
            "system": [i.to_dict() for i in self.system],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, session_id: str, data: dict[str, Any]) -> "ChatMemory":
        working_raw = data.get("working")
        if working_raw is None:
            working_raw = data.get("turns") or []
        memory = cls(
            session_id=session_id,
            working=[ChatTurn.from_dict(t) for t in working_raw],
            episodic=[MemoryItem.from_dict(i) for i in data.get("episodic") or []],
            semantic=[MemoryItem.from_dict(i) for i in data.get("semantic") or []],
            long_term=[MemoryItem.from_dict(i) for i in data.get("long_term") or []],
            system=[MemoryItem.from_dict(i) for i in data.get("system") or []],
            metadata=data.get("metadata") or {},
        )
        memory._compact_working()
        return memory

    # --- internals ---

    def _last_user_text(self) -> str:
        for turn in reversed(self.working):
            if turn.role == "user":
                return turn.content
        return ""

    def _append_working(self, turn: ChatTurn) -> None:
        self.working.append(turn)
        self._compact_working()

    def _compact_working(self) -> None:
        while len(self.working) > self.WORKING_LIMIT:
            old = self.working.pop(0)
            self.episodic.append(
                MemoryItem(
                    kind=MemoryKind.EPISODIC.value,
                    role=old.role,
                    content=old.content,
                    created_at=old.created_at,
                    metadata=old.metadata,
                    keywords=sorted(_tokenize(old.content)),
                )
            )
        if len(self.episodic) > self.EPISODIC_LIMIT:
            self.episodic = self.episodic[-self.EPISODIC_LIMIT :]

    def _upsert_fact(
        self,
        bucket: list[MemoryItem],
        item: MemoryItem,
        limit: int,
    ) -> None:
        key = item.content.strip().lower()
        for existing in bucket:
            if existing.content.strip().lower() == key:
                existing.keywords = item.keywords
                existing.metadata = {**existing.metadata, **item.metadata}
                existing.created_at = item.created_at
                return
        bucket.append(item)
        if len(bucket) > limit:
            del bucket[0 : len(bucket) - limit]

    def _extract_and_store_facts(self, content: str) -> None:
        text = content.strip()
        if not text:
            return

        facts: list[tuple[str, list[str], bool]] = []

        height = re.search(r"(?:cao|chiều cao)\s*[:=]?\s*(\d(?:[.,]\d+)?\s*m(?:\d+)?)|\b(1[m\s]?\d{1,2})\b", text, re.I)
        if height:
            value = (height.group(1) or height.group(2) or "").strip()
            if value:
                facts.append((f"Chiều cao khách: {value}", ["chiều cao", "cao", "size"], True))

        weight = re.search(r"(?:nặng|cân nặng)\s*[:=]?\s*(\d{2,3})\s*kg|\b(\d{2,3})\s*kg\b", text, re.I)
        if weight:
            value = (weight.group(1) or weight.group(2) or "").strip()
            if value:
                facts.append((f"Cân nặng khách: {value}kg", ["cân nặng", "nặng", "size"], True))

        size = re.search(
            r"(?:size|kích cỡ|cỡ)\s*[:=]?\s*(s|m|l|xl|xxl|\d{2})",
            text,
            re.I,
        )
        if size:
            value = size.group(1).upper()
            facts.append((f"Size ưa thích/phù hợp: {value}", ["size", "kích cỡ", value.lower()], True))

        color = re.search(
            r"(?:thích|ưu tiên|màu)\s+(đen|trắng|be|xám|navy|xanh|đỏ|hồng|nâu|kem)",
            text,
            re.I,
        )
        if color:
            value = color.group(1).lower()
            facts.append((f"Màu ưa thích: {value}", ["màu", value], True))

        for fact, keywords, promote in facts:
            self.add_semantic_fact(fact, keywords=keywords, promote_long_term=promote)
