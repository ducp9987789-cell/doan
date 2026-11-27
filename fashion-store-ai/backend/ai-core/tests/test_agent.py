import asyncio

from agents.shopping_agent import ShoppingAgent
from llm.factory import FallbackLLM
from tool.base import Tool
from tool.mcp import FashionMcpServer


class FakeRetriever(Tool):
    name = "fake_retriever"

    async def run(self, query: str, n_results: int = 5, **_):
        return [{"text": f"Context for {query}", "metadata": {"type": "faq"}, "distance": 0.1}]


class FakeDb:
    class _Cursor:
        def __init__(self, items):
            self._items = items

        def limit(self, _n):
            return self

        def __aiter__(self):
            async def _gen():
                for item in self._items:
                    yield item

            return _gen()

        async def to_list(self, length=100):
            return self._items[:length]

    class products:
        @staticmethod
        def find(_query):
            return FakeDb._Cursor(
                [
                    {
                        "_id": "1",
                        "name": "Áo sơ mi",
                        "price": 199000,
                        "sale_price": None,
                        "images": [None],
                    }
                ]
            )

    class store_info:
        @staticmethod
        async def find_one(_query):
            return {
                "store_name": "Fashion Store AI",
                "hotline": "1900",
                "email": "a@b.c",
                "address": "HN",
                "shipping_policy": "2-4 ngày",
                "return_policy": "7 ngày",
                "about": "Demo",
            }

    class promotions:
        @staticmethod
        def find(_query):
            return FakeDb._Cursor([])

    class faqs:
        @staticmethod
        def find(_query):
            return FakeDb._Cursor([])


def test_shopping_agent_fallback_answer():
    mcp = FashionMcpServer(db_getter=lambda: FakeDb)
    agent = ShoppingAgent(llm=FallbackLLM(), retriever=FakeRetriever(), mcp=mcp)
    result = asyncio.run(agent.run("Gợi ý áo sơ mi", session_id="s1"))
    assert result.answer
    assert result.suggested_products
    assert result.sources
    assert result.metadata.get("complexity") == "complex"
    assert "product_search" in result.metadata.get("mcp_tools", [])


def test_shopping_agent_simple_greeting_skips_tools():
    mcp = FashionMcpServer(db_getter=lambda: FakeDb)
    agent = ShoppingAgent(llm=FallbackLLM(), retriever=FakeRetriever(), mcp=mcp)
    result = asyncio.run(agent.run("Xin chào", session_id="s2"))
    assert result.answer
    assert result.suggested_products == []
    assert result.sources == []
    assert result.metadata.get("complexity") == "simple"
    assert result.metadata.get("tool_mode") == "none"
    assert result.metadata.get("prompt_kind") == "simple_fallback"


def test_shopping_agent_simple_weather_skips_tools():
    mcp = FashionMcpServer(db_getter=lambda: FakeDb)
    agent = ShoppingAgent(llm=FallbackLLM(), retriever=FakeRetriever(), mcp=mcp)
    result = asyncio.run(agent.run("Thời tiết đẹp không", session_id="s3"))
    assert result.answer
    assert result.metadata.get("complexity") == "simple"
    assert result.metadata.get("tool_mode") == "none"
