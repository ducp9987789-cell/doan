import asyncio

from agents.shopping_agent import ShoppingAgent
from llm.factory import FallbackLLM
from tool.base import Tool


class FakeRetriever(Tool):
    name = "fake_retriever"

    async def run(self, query: str, n_results: int = 5, **_):
        return [{"text": f"Context for {query}", "metadata": {"type": "faq"}, "distance": 0.1}]


class FakeProductSearch(Tool):
    name = "fake_product_search"

    async def run(self, query: str, limit: int = 3, **_):
        return [{"id": "1", "name": "Áo sơ mi", "price": 199000, "sale_price": None, "image": None}]


def test_shopping_agent_fallback_answer():
    agent = ShoppingAgent(llm=FallbackLLM(), retriever=FakeRetriever(), product_search=FakeProductSearch())
    result = asyncio.run(agent.run("Gợi ý áo sơ mi", session_id="s1"))
    assert result.answer
    assert result.suggested_products
    assert result.sources
