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
        
        # Đồng bộ thông tin stock mới nhất của từng sản phẩm
        for item in items:
            try:
                p = await db.products.find_one({"_id": to_object_id(item["product_id"])})
                if p:
                    item["stock"] = p.get("stock", 0)
            except Exception:
                pass

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
            raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
        
        available_stock = product.get("stock", 0)
        # Nếu sản phẩm có phân loại biến thể, lấy tồn kho theo biến thể cụ thể
        variants = product.get("variants") or []
        req_color = (payload.color or "").strip()
        req_size = (payload.size or "").strip()
        if variants and (req_color or req_size):
            for v in variants:
                v_col = (v.get("color") or "").strip()
                v_sz = (v.get("size") or "").strip()
                if (not req_color or v_col.lower() == req_color.lower()) and \
                   (not req_size or v_sz.upper() == req_size.upper()):
                    available_stock = v.get("stock", 0)
                    break

        if available_stock <= 0:
            raise HTTPException(status_code=400, detail="Sản phẩm này hiện đã hết hàng.")

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
                new_qty = item["quantity"] + payload.quantity
                if new_qty > available_stock:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Số lượng yêu cầu ({new_qty}) vượt quá số lượng còn lại trong kho ({available_stock} sản phẩm)."
                    )
                item["quantity"] = new_qty
                item["stock"] = available_stock
                matched = True
                break
        if not matched:
            if payload.quantity > available_stock:
                raise HTTPException(
                    status_code=400,
                    detail=f"Số lượng yêu cầu ({payload.quantity}) vượt quá số lượng còn lại trong kho ({available_stock} sản phẩm)."
                )
            items.append(
                {
                    "product_id": payload.product_id,
                    "name": product["name"],
                    "price": price,
                    "quantity": payload.quantity,
                    "color": payload.color,
                    "size": payload.size,
                    "image": (product.get("images") or [None])[0],
                    "stock": available_stock,
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

        available_stock = 999999
        if quantity > 0:
            product = await db.products.find_one({"_id": to_object_id(product_id), "is_active": True})
            if not product:
                raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
            available_stock = product.get("stock", 0)
            if available_stock <= 0:
                raise HTTPException(status_code=400, detail="Sản phẩm này hiện đã hết hàng.")
            if quantity > available_stock:
                raise HTTPException(
                    status_code=400,
                    detail=f"Số lượng yêu cầu ({quantity}) vượt quá số lượng còn lại trong kho ({available_stock} sản phẩm)."
                )

        items = []
        for item in cart.get("items", []):
            if (
                item["product_id"] == product_id
                and item.get("color") == color
                and item.get("size") == size
            ):
                if quantity > 0:
                    item["quantity"] = quantity
                    item["stock"] = available_stock
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
            raise HTTPException(status_code=400, detail="Giỏ hàng đang trống")
        
        db = get_database()

        # Kiểm tra tồn kho trước khi đặt hàng
        for item in cart["items"]:
            prod = await db.products.find_one({"_id": to_object_id(item["product_id"])})
            if not prod or not prod.get("is_active", True):
                raise HTTPException(
                    status_code=400,
                    detail=f"Sản phẩm '{item.get('name')}' hiện không còn kinh doanh."
                )
            avail_stock = prod.get("stock", 0)
            if avail_stock <= 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Sản phẩm '{item.get('name')}' hiện đã hết hàng."
                )
            if item["quantity"] > avail_stock:
                raise HTTPException(
                    status_code=400,
                    detail=f"Sản phẩm '{item.get('name')}' chỉ còn {avail_stock} sản phẩm trong kho (bạn đặt {item['quantity']})."
                )

            # Kiểm tra tồn kho theo từng biến thể (màu sắc, size) nếu có
            variants = prod.get("variants") or []
            item_color = (item.get("color") or "").strip()
            item_size = (item.get("size") or "").strip()
            if variants and (item_color or item_size):
                for v in variants:
                    v_col = (v.get("color") or "").strip()
                    v_sz = (v.get("size") or "").strip()
                    if (not item_color or v_col.lower() == item_color.lower()) and \
                       (not item_size or v_sz.upper() == item_size.upper()):
                        var_stock = v.get("stock", 0)
                        if var_stock <= 0:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Sản phẩm '{item.get('name')}' (màu {item_color}, size {item_size}) hiện đã hết hàng."
                            )
                        if item["quantity"] > var_stock:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Sản phẩm '{item.get('name')}' (màu {item_color}, size {item_size}) chỉ còn {var_stock} sản phẩm trong kho (bạn đặt {item['quantity']})."
                            )
                        break

        subtotal = cart["subtotal"]
        discount, promo_code = await OrderService._resolve_promotion(payload.promotion_code, subtotal)
        shipping_fee = 30000 if subtotal - discount < 500000 else 0
        total = subtotal - discount + shipping_fee

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

        # Trừ tồn kho sau khi đặt hàng thành công
        for item in cart["items"]:
            try:
                prod_oid = to_object_id(item["product_id"])
                qty = int(item["quantity"])
                item_color = (item.get("color") or "").strip()
                item_size = (item.get("size") or "").strip()

                # 1. Trừ tồn kho biến thể tương ứng nếu sản phẩm có biến thể
                if item_color and item_size:
                    await db.products.update_one(
                        {
                            "_id": prod_oid,
                            "variants": {
                                "$elemMatch": {
                                    "color": {"$regex": f"^{item_color}$", "$options": "i"},
                                    "size": {"$regex": f"^{item_size}$", "$options": "i"}
                                }
                            }
                        },
                        {"$inc": {"variants.$.stock": -qty}}
                    )

                # 2. Trừ tổng tồn kho sản phẩm
                await db.products.update_one(
                    {"_id": prod_oid},
                    {"$inc": {"stock": -qty}}
                )
            except Exception:
                pass

        await OrderService.clear_cart(user_id)
        return serialize_doc(doc)

    @staticmethod
    async def list_orders(user_id: Optional[str] = None) -> list[dict[str, Any]]:
        db = get_database()
        query: dict[str, Any] = {}
        if user_id:
            from bson import ObjectId
            if ObjectId.is_valid(user_id):
                query["$or"] = [{"user_id": str(user_id)}, {"user_id": ObjectId(user_id)}]
            else:
                query["user_id"] = str(user_id)
        cursor = db.orders.find(query).sort("created_at", -1)
        return [serialize_doc(doc) for doc in await cursor.to_list(length=200)]

    @staticmethod
    async def get_order(order_id: str, user_id: Optional[str] = None, is_admin: bool = False) -> dict[str, Any]:
        db = get_database()
        doc = await db.orders.find_one({"_id": to_object_id(order_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Order not found")
        if not is_admin and str(doc.get("user_id")) != str(user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return serialize_doc(doc)

    @staticmethod
    async def update_order_status(order_id: str, status_value: str) -> dict[str, Any]:
        allowed = {"pending", "confirmed", "shipping", "completed", "cancelled"}
        if status_value not in allowed:
            raise HTTPException(status_code=400, detail="Invalid order status")

        # Thứ tự trạng thái: trạng thái chỉ được chuyển tiến, không được chuyển ngược
        status_order = ["pending", "confirmed", "shipping", "completed"]

        db = get_database()
        order = await db.orders.find_one({"_id": to_object_id(order_id)})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        current_status = order.get("status", "pending")

        # Không thể thay đổi trạng thái của đơn đã hoàn thành hoặc đã hủy
        if current_status in ("completed", "cancelled"):
            raise HTTPException(
                status_code=400,
                detail=f"Không thể thay đổi trạng thái đơn hàng đã '{current_status}'"
            )

        # Không cho phép chuyển ngược (chỉ huỷ là ngoại lệ từ bất kỳ trạng thái nào)
        if status_value != "cancelled":
            current_idx = status_order.index(current_status) if current_status in status_order else -1
            new_idx = status_order.index(status_value) if status_value in status_order else -1
            if new_idx < current_idx:
                status_labels = {
                    "pending": "Chờ xác nhận",
                    "confirmed": "Đã duyệt đơn",
                    "shipping": "Đang giao hàng",
                    "completed": "Giao thành công",
                }
                raise HTTPException(
                    status_code=400,
                    detail=f"Không thể chuyển trạng thái từ '{status_labels.get(current_status, current_status)}' về '{status_labels.get(status_value, status_value)}'. Trạng thái chỉ được chuyển tiến."
                )

        result = await db.orders.find_one_and_update(
            {"_id": to_object_id(order_id)},
            {"$set": {"status": status_value, "updated_at": datetime.utcnow()}},
            return_document=ReturnDocument.AFTER,
        )
        if not result:
            raise HTTPException(status_code=404, detail="Order not found")
        return serialize_doc(result)
