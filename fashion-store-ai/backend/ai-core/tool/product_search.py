from __future__ import annotations

import re
from typing import Any

from tool.base import Tool

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
