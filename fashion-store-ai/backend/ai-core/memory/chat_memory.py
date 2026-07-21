from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChatTurn:
    role: str
    content: str


@dataclass
class ChatMemory:
    """In-session conversation memory for the shopping agent."""

    session_id: str
    turns: list[ChatTurn] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_user(self, content: str) -> None:
        self.turns.append(ChatTurn(role="user", content=content))

    def add_assistant(self, content: str) -> None:
        self.turns.append(ChatTurn(role="assistant", content=content))

    def recent(self, limit: int = 6) -> list[ChatTurn]:
        return self.turns[-limit:]

    def as_text(self, limit: int = 6) -> str:
        lines = [f"{turn.role}: {turn.content}" for turn in self.recent(limit)]
        return "\n".join(lines)
