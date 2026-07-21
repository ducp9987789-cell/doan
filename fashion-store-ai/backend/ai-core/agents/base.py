from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class AgentResult:
    answer: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    suggested_products: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    name: str = "base_agent"

    @abstractmethod
    async def run(self, message: str, *, session_id: Optional[str] = None) -> AgentResult:
        raise NotImplementedError
