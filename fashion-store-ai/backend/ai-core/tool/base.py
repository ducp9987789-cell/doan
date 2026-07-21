from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    name: str = "tool"
    description: str = ""

    @abstractmethod
    async def run(self, **kwargs: Any) -> Any:
        raise NotImplementedError
