import asyncio

from llm.embeddings import LocalEmbeddingProvider


def test_local_embedding_is_deterministic():
    provider = LocalEmbeddingProvider()
    first = asyncio.run(provider.embed(["áo sơ mi"]))
    second = asyncio.run(provider.embed(["áo sơ mi"]))
    assert first == second
    assert len(first[0]) == 64


def test_local_embedding_differs_by_text():
    provider = LocalEmbeddingProvider()
    a = asyncio.run(provider.embed(["áo"]))
    b = asyncio.run(provider.embed(["quần"]))
    assert a != b
