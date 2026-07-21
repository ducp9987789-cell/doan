from __future__ import annotations

import logging
from typing import Optional

from llm.base import LLMProvider

logger = logging.getLogger(__name__)


class GeminiLLM(LLMProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, *, system: Optional[str] = None, temperature: float = 0.4) -> str:
        import google.generativeai as genai

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model)
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = model.generate_content(full_prompt)
        return response.text or ""
