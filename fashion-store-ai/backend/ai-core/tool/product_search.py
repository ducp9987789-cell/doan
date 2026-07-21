from __future__ import annotations

import re
from typing import Any, Optional

from tool.base import Tool


class ProductSearchTool(Tool):
    name = "product_search"
    description = "Search active products by keyword for chatbot suggestions."

    def __init__(self, db_getter: Any) -> None:
        self.db_getter = db_getter

    async def run(self, query: str, limit: int = 3, **_: Any) -> list[dict[str, Any]]:
        db = self.db_getter()
        tokens = [token for token in re.findall(r"\w+", query.lower()) if len(token) > 2]
        mongo_query: dict[str, Any] = {"is_active": True}
        if tokens:
            mongo_query["$or"] = [
                {"name": {"$regex": "|".join(tokens), "$options": "i"}},
                {"tags": {"$regex": "|".join(tokens), "$options": "i"}},
                {"description": {"$regex": "|".join(tokens), "$options": "i"}},
                {"category_name": {"$regex": "|".join(tokens), "$options": "i"}},
            ]

        products = await self._fetch(db, mongo_query, limit)
        if products:
            return products
        return await self._fetch(db, {"is_active": True, "is_featured": True}, limit)

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
