from __future__ import annotations

import logging
from typing import Optional

from llm.base import LLMProvider

logger = logging.getLogger(__name__)


class GeminiLLM(LLMProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model.replace("models/", "") if model else "gemini-3.5-flash"

    async def generate(self, prompt: str, *, system: Optional[str] = None, temperature: float = 0.4) -> str:
        import google.generativeai as genai

        genai.configure(api_key=self.api_key)
        full_prompt = f"{system}\n\n{prompt}" if system else prompt

        candidate_models = [self.model, "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"]
        # Deduplicate while preserving order
        unique_models = list(dict.fromkeys(candidate_models))

        last_error = None
        for m_name in unique_models:
            try:
                model = genai.GenerativeModel(m_name)
                response = model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(temperature=temperature),
                )
                if hasattr(response, "text") and response.text:
                    return response.text.strip()
                if hasattr(response, "candidates") and response.candidates:
                    parts = response.candidates[0].content.parts
                    text_parts = [p.text for p in parts if hasattr(p, "text") and p.text]
                    if text_parts:
                        return "".join(text_parts).strip()
            except Exception as exc:  # noqa: BLE001
                logger.warning("Gemini model '%s' failed: %s. Trying fallback...", m_name, exc)
                last_error = exc

        logger.error("All Gemini candidate models failed: %s", last_error)
        return ""

