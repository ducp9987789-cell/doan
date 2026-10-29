from __future__ import annotations

import hashlib
import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class LocalEmbeddingProvider(EmbeddingProvider):
    """Deterministic local embedding fallback when no API key is configured."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            values: list[float] = []
            seed = digest
            while len(values) < 64:
                seed = hashlib.sha256(seed).digest()
                values.extend(b / 255.0 for b in seed)
            vectors.append(values[:64])
        return vectors


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model
        self._fallback = LocalEmbeddingProvider()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            response = client.embeddings.create(model=self.model, input=texts)
            return [item.embedding for item in response.data]
        except Exception as exc:  # noqa: BLE001
            logger.warning("OpenAI embedding failed, using local fallback: %s", exc)
            return await self._fallback.embed(texts)


class GeminiEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self._fallback = LocalEmbeddingProvider()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            embeddings = []
            # Try gemini-embedding-001 first, fallback to gemini-embedding-2
            candidate_models = ["models/gemini-embedding-001", "models/gemini-embedding-2"]
            used_model = None

            for m in candidate_models:
                try:
                    res = genai.embed_content(model=m, content=texts[0])
                    if "embedding" in res:
                        used_model = m
                        break
                except Exception:
                    continue

            if not used_model:
                used_model = "models/gemini-embedding-001"

            for text in texts:
                result = genai.embed_content(model=used_model, content=text)
                embeddings.append(result["embedding"])
            return embeddings
        except Exception as exc:  # noqa: BLE001
            logger.warning("Gemini embedding failed, using local fallback: %s", exc)
            return await self._fallback.embed(texts)


def get_embedding_provider(
    *,
    provider: str,
    openai_api_key: str = "",
    openai_embedding_model: str = "text-embedding-3-small",
    gemini_api_key: str = "",
) -> EmbeddingProvider:
    name = provider.lower()
    if name == "openai" and openai_api_key:
        return OpenAIEmbeddingProvider(openai_api_key, openai_embedding_model)
    if (name == "gemini" or not openai_api_key) and gemini_api_key:
        return GeminiEmbeddingProvider(gemini_api_key)
    if openai_api_key:
        return OpenAIEmbeddingProvider(openai_api_key, openai_embedding_model)
    return LocalEmbeddingProvider()
