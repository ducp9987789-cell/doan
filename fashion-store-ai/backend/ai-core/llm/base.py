from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, *, system: Optional[str] = None, temperature: float = 0.4) -> str:
        raise NotImplementedError
