from datetime import datetime
from typing import Any, Optional

from pymongo import ReturnDocument
from fastapi import HTTPException, status

from app.core.utils import serialize_doc, to_object_id
from app.db.mongodb import get_database
from app.schemas.order import CartItemCreate, OrderCreate


class OrderService:
    @staticmethod
    async def get_cart(user_id: str) -> dict[str, Any]:
        db = get_database()
        cart = await db.carts.find_one({"user_id": user_id})
        if not cart:
            cart = {"user_id": user_id, "items": [], "updated_at": datetime.utcnow()}
            result = await db.carts.insert_one(cart)
            cart["_id"] = result.inserted_id
        items = cart.get("items", [])
        subtotal = sum(item["price"] * item["quantity"] for item in items)
        return {
            "user_id": user_id,
            "items": items,
            "subtotal": subtotal,
            "item_count": sum(item["quantity"] for item in items),
        }

    @staticmethod
    async def add_to_cart(user_id: str, payload: CartItemCreate) -> dict[str, Any]:
        db = get_database()
        product = await db.products.find_one({"_id": to_object_id(payload.product_id), "is_active": True})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        price = product.get("sale_price") or product["price"]
        cart = await db.carts.find_one({"user_id": user_id})
        items = cart["items"] if cart else []
        matched = False
        for item in items:
            if (
                item["product_id"] == payload.product_id
                and item.get("color") == payload.color
                and item.get("size") == payload.size
            ):
                item["quantity"] += payload.quantity
                matched = True
                break
        if not matched:
            items.append(
                {
                    "product_id": payload.product_id,
                    "name": product["name"],
                    "price": price,
                    "quantity": payload.quantity,
                    "color": payload.color,
                    "size": payload.size,
                    "image": (product.get("images") or [None])[0],
                }
            )
        await db.carts.update_one(
            {"user_id": user_id},
            {"$set": {"items": items, "updated_at": datetime.utcnow()}},
            upsert=True,
        )
        return await OrderService.get_cart(user_id)

    @staticmethod
    async def update_cart_item(
        user_id: str,
        product_id: str,
        quantity: int,
        color: Optional[str] = None,
        size: Optional[str] = None,
    ) -> dict[str, Any]:
        db = get_database()
        cart = await db.carts.find_one({"user_id": user_id})
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        items = []
        for item in cart.get("items", []):
            if (
                item["product_id"] == product_id
                and item.get("color") == color
                and item.get("size") == size
            ):
                if quantity > 0:
                    item["quantity"] = quantity
                    items.append(item)
            else:
                items.append(item)
        await db.carts.update_one(
            {"user_id": user_id},
            {"$set": {"items": items, "updated_at": datetime.utcnow()}},
        )
        return await OrderService.get_cart(user_id)

    @staticmethod
    async def clear_cart(user_id: str) -> None:
        db = get_database()
        await db.carts.update_one(
            {"user_id": user_id},
            {"$set": {"items": [], "updated_at": datetime.utcnow()}},
            upsert=True,
        )

    @staticmethod
    async def _resolve_promotion(code: Optional[str], subtotal: float) -> tuple[float, Optional[str]]:
        if not code:
            return 0.0, None
        db = get_database()
        promo = await db.promotions.find_one({"code": code.upper(), "is_active": True})
        if not promo:
            raise HTTPException(status_code=400, detail="Invalid promotion code")
        if subtotal < promo.get("min_order_value", 0):
            raise HTTPException(status_code=400, detail="Order value does not meet promotion minimum")
        if promo.get("discount_type") == "percent":
            discount = round(subtotal * promo["discount_value"] / 100, 2)
        else:
            discount = float(promo["discount_value"])
        return min(discount, subtotal), promo["code"]

    @staticmethod
    async def create_order(user_id: str, payload: OrderCreate) -> dict[str, Any]:
        cart = await OrderService.get_cart(user_id)
        if not cart["items"]:
            raise HTTPException(status_code=400, detail="Cart is empty")
        subtotal = cart["subtotal"]
        discount, promo_code = await OrderService._resolve_promotion(payload.promotion_code, subtotal)
        shipping_fee = 30000 if subtotal - discount < 500000 else 0
        total = subtotal - discount + shipping_fee
        db = get_database()
        doc = {
            "user_id": user_id,
            "items": cart["items"],
            "shipping_address": payload.shipping_address.model_dump(),
            "payment_method": payload.payment_method,
            "status": "pending",
            "subtotal": subtotal,
            "discount": discount,
            "shipping_fee": shipping_fee,
            "total": total,
            "promotion_code": promo_code,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db.orders.insert_one(doc)
        doc["_id"] = result.inserted_id
        await OrderService.clear_cart(user_id)
        return serialize_doc(doc)

    @staticmethod
    async def list_orders(user_id: Optional[str] = None) -> list[dict[str, Any]]:
        db = get_database()
        query: dict[str, Any] = {}
        if user_id:
            query["user_id"] = user_id
        cursor = db.orders.find(query).sort("created_at", -1)
        return [serialize_doc(doc) for doc in await cursor.to_list(length=200)]

    @staticmethod
    async def get_order(order_id: str, user_id: Optional[str] = None, is_admin: bool = False) -> dict[str, Any]:
        db = get_database()
        doc = await db.orders.find_one({"_id": to_object_id(order_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Order not found")
        if not is_admin and doc["user_id"] != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return serialize_doc(doc)

    @staticmethod
    async def update_order_status(order_id: str, status_value: str) -> dict[str, Any]:
        allowed = {"pending", "confirmed", "shipping", "completed", "cancelled"}
        if status_value not in allowed:
            raise HTTPException(status_code=400, detail="Invalid order status")
        db = get_database()
        result = await db.orders.find_one_and_update(
            {"_id": to_object_id(order_id)},
            {"$set": {"status": status_value, "updated_at": datetime.utcnow()}},
            return_document=ReturnDocument.AFTER,
        )
        if not result:
            raise HTTPException(status_code=404, detail="Order not found")
        return serialize_doc(result)
