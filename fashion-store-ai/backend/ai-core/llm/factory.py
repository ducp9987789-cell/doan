from __future__ import annotations

import logging
from typing import Optional

from llm.base import LLMProvider
from llm.gemini_llm import GeminiLLM
from llm.openai_llm import OpenAILLM

logger = logging.getLogger(__name__)


class FallbackLLM(LLMProvider):
    """Demo-mode LLM used when no provider API key is configured."""

    async def generate(self, prompt: str, *, system: Optional[str] = None, temperature: float = 0.4) -> str:
        return ""


def get_llm_provider(
    *,
    provider: str,
    openai_api_key: str = "",
    openai_model: str = "gpt-4o-mini",
    gemini_api_key: str = "",
    gemini_model: str = "gemini-1.5-flash",
) -> LLMProvider:
    name = provider.lower()
    if name == "openai" and openai_api_key:
        return OpenAILLM(openai_api_key, openai_model)
    if name == "gemini" and gemini_api_key:
        return GeminiLLM(gemini_api_key, gemini_model)
    logger.info("No LLM API key configured, using fallback demo mode")
    return FallbackLLM()
