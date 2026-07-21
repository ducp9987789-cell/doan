from __future__ import annotations

import logging
from typing import Optional

from llm.base import LLMProvider

logger = logging.getLogger(__name__)


class OpenAILLM(LLMProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, *, system: Optional[str] = None, temperature: float = 0.4) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""
