"""MCP tools — công cụ có cấu trúc theo kiểu Model Context Protocol.

Phân biệt với RAG (`tool/rag.py`):
- MCP: list_tools / call_tool trên dữ liệu nghiệp vụ (MongoDB).
- RAG: truy xuất ngữ cảnh từ vector store.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional

from tool.base import Tool

logger = logging.getLogger(__name__)

# Từ dừng tiếng Việt / tiếng Anh thường gặp trong câu hỏi chatbot
_STOPWORDS = {
    "cái",
    "này",
    "kia",
    "cho",
    "tôi",
    "mình",
    "bạn",
    "là",
    "của",
    "và",
    "với",
    "có",
    "không",
    "gì",
    "như",
    "thế",
    "nào",
    "muốn",
    "cần",
    "một",
    "các",
    "được",
    "trong",
    "khi",
    "để",
    "về",
    "hay",
    "hoặc",
    "giúp",
    "xin",
    "vui",
    "lòng",
    "the",
    "and",
    "for",
    "with",
    "please",
}

__all__ = [
    "ProductSearchTool",
    "StoreInfoTool",
    "PromotionLookupTool",
    "FaqLookupTool",
    "FashionMcpServer",
]


class ProductSearchTool(Tool):
    name = "product_search"
    description = "Search active products by keyword for chatbot suggestions."

    def __init__(self, db_getter: Any) -> None:
        self.db_getter = db_getter

    @staticmethod
    def extract_keywords(query: str) -> list[str]:
        tokens = [token for token in re.findall(r"\w+", query.lower()) if len(token) > 2]
        return [token for token in tokens if token not in _STOPWORDS]

    async def run(self, query: str, limit: int = 3, **_: Any) -> list[dict[str, Any]]:
        db = self.db_getter()
        tokens = self.extract_keywords(query)
        mongo_query: dict[str, Any] = {"is_active": True}
        if tokens:
            pattern = "|".join(re.escape(token) for token in tokens)
            mongo_query["$or"] = [
                {"name": {"$regex": pattern, "$options": "i"}},
                {"tags": {"$regex": pattern, "$options": "i"}},
                {"description": {"$regex": pattern, "$options": "i"}},
                {"category_name": {"$regex": pattern, "$options": "i"}},
            ]

        products = await self._fetch(db, mongo_query, limit)
        if products:
            return products
        # Chỉ fallback featured khi vẫn còn từ khóa sản phẩm; tránh trả thẻ SP cho câu hỏi chung
        if tokens:
            return await self._fetch(db, {"is_active": True, "is_featured": True}, limit)
        return []

    async def _fetch(self, db: Any, query: dict[str, Any], limit: int) -> list[dict[str, Any]]:
        cursor = db.products.find(query).limit(limit)
        products: list[dict[str, Any]] = []
        async for product in cursor:
            products.append(
                {
                    "id": str(product["_id"]),
                    "name": product["name"],
                    "price": product["price"],
                    "sale_price": product.get("sale_price"),
                    "image": (product.get("images") or [None])[0],
                }
            )
        return products


class StoreInfoTool(Tool):
    name = "get_store_info"
    description = "Get store contact info, shipping and return policies from MongoDB."

    def __init__(self, db_getter: Any) -> None:
        self.db_getter = db_getter

    async def run(self, **_: Any) -> dict[str, Any]:
        db = self.db_getter()
        store = await db.store_info.find_one({})
        if not store:
            return {}
        store.pop("_id", None)
        return {
            "store_name": store.get("store_name"),
            "hotline": store.get("hotline"),
            "email": store.get("email"),
            "address": store.get("address"),
            "shipping_policy": store.get("shipping_policy"),
            "return_policy": store.get("return_policy"),
            "about": store.get("about"),
        }


class PromotionLookupTool(Tool):
    name = "lookup_promotion"
    description = "Lookup active promotion codes / vouchers by keyword or code."

    def __init__(self, db_getter: Any) -> None:
        self.db_getter = db_getter

    async def run(self, query: str = "", limit: int = 5, **_: Any) -> list[dict[str, Any]]:
        db = self.db_getter()
        mongo_query: dict[str, Any] = {"is_active": True}
        text = (query or "").strip()
        if text:
            pattern = re.escape(text)
            mongo_query["$or"] = [
                {"code": {"$regex": pattern, "$options": "i"}},
                {"title": {"$regex": pattern, "$options": "i"}},
                {"description": {"$regex": pattern, "$options": "i"}},
            ]

        cursor = db.promotions.find(mongo_query).limit(limit)
        promotions: list[dict[str, Any]] = []
        async for promo in cursor:
            promotions.append(
                {
                    "code": promo.get("code"),
                    "title": promo.get("title"),
                    "description": promo.get("description"),
                    "discount_type": promo.get("discount_type"),
                    "discount_value": promo.get("discount_value"),
                    "min_order_value": promo.get("min_order_value", 0),
                }
            )
        return promotions


class FaqLookupTool(Tool):
    name = "lookup_faq"
    description = "Lookup active FAQ entries by keyword."

    def __init__(self, db_getter: Any) -> None:
        self.db_getter = db_getter

    async def run(self, query: str = "", limit: int = 5, **_: Any) -> list[dict[str, Any]]:
        db = self.db_getter()
        mongo_query: dict[str, Any] = {"is_active": True}
        text = (query or "").strip()
        if text:
            pattern = re.escape(text)
            mongo_query["$or"] = [
                {"question": {"$regex": pattern, "$options": "i"}},
                {"answer": {"$regex": pattern, "$options": "i"}},
                {"category": {"$regex": pattern, "$options": "i"}},
            ]

        cursor = db.faqs.find(mongo_query).limit(limit)
        faqs: list[dict[str, Any]] = []
        async for faq in cursor:
            faqs.append(
                {
                    "question": faq.get("question"),
                    "answer": faq.get("answer"),
                    "category": faq.get("category", "general"),
                }
            )
        return faqs


class FashionMcpServer:
    """Local MCP-style tool server: list_tools() + call_tool(name, arguments)."""

    def __init__(self, db_getter: Any) -> None:
        self.product_search = ProductSearchTool(db_getter)
        self.store_info = StoreInfoTool(db_getter)
        self.promotion_lookup = PromotionLookupTool(db_getter)
        self.faq_lookup = FaqLookupTool(db_getter)
        self._tools: dict[str, Tool] = {
            self.product_search.name: self.product_search,
            self.store_info.name: self.store_info,
            self.promotion_lookup.name: self.promotion_lookup,
            self.faq_lookup.name: self.faq_lookup,
        }

    def list_tools(self) -> list[dict[str, str]]:
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self._tools.values()
        ]

    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    async def call_tool(self, name: str, arguments: Optional[dict[str, Any]] = None) -> Any:
        tool = self._tools.get(name)
        if tool is None:
            raise ValueError(f"Unknown MCP tool: {name}")
        args = arguments or {}
        try:
            return await tool.run(**args)
        except Exception as exc:  # noqa: BLE001
            logger.warning("MCP tool '%s' failed: %s", name, exc)
            raise

    async def search_products(self, query: str, limit: int = 3) -> list[dict[str, Any]]:
        return await self.call_tool("product_search", {"query": query, "limit": limit})

    async def get_store_info(self) -> dict[str, Any]:
        return await self.call_tool("get_store_info", {})

    async def lookup_promotions(self, query: str = "", limit: int = 5) -> list[dict[str, Any]]:
        return await self.call_tool("lookup_promotion", {"query": query, "limit": limit})

    async def lookup_faqs(self, query: str = "", limit: int = 5) -> list[dict[str, Any]]:
        return await self.call_tool("lookup_faq", {"query": query, "limit": limit})
