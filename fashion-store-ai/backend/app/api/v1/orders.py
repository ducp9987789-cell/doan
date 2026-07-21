from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_admin, get_current_user
from app.schemas.order import (
    CartItemCreate,
    CartItemUpdate,
    CartResponse,
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
)
from app.services.order_service import OrderService

router = APIRouter(tags=["orders"])


@router.get("/cart", response_model=CartResponse)
async def get_cart(current_user: dict = Depends(get_current_user)) -> dict:
    return await OrderService.get_cart(current_user["id"])


@router.post("/cart/items", response_model=CartResponse)
async def add_cart_item(payload: CartItemCreate, current_user: dict = Depends(get_current_user)) -> dict:
    return await OrderService.add_to_cart(current_user["id"], payload)


@router.patch("/cart/items/{product_id}", response_model=CartResponse)
async def update_cart_item(
    product_id: str,
    payload: CartItemUpdate,
    color: Optional[str] = None,
    size: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
) -> dict:
    return await OrderService.update_cart_item(
        current_user["id"], product_id, payload.quantity, color=color, size=size
    )


@router.delete("/cart", response_model=CartResponse)
async def clear_cart(current_user: dict = Depends(get_current_user)) -> dict:
    await OrderService.clear_cart(current_user["id"])
    return await OrderService.get_cart(current_user["id"])


@router.post("/orders", response_model=OrderResponse)
async def create_order(payload: OrderCreate, current_user: dict = Depends(get_current_user)) -> dict:
    return await OrderService.create_order(current_user["id"], payload)


@router.get("/orders", response_model=list[OrderResponse])
async def list_my_orders(current_user: dict = Depends(get_current_user)) -> list[dict]:
    return await OrderService.list_orders(user_id=current_user["id"])


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    is_admin = current_user.get("role") == "admin"
    return await OrderService.get_order(order_id, user_id=current_user["id"], is_admin=is_admin)


@router.get("/admin/orders", response_model=list[OrderResponse], dependencies=[Depends(get_current_admin)])
async def admin_list_orders() -> list[dict]:
    return await OrderService.list_orders()


@router.patch("/admin/orders/{order_id}", response_model=OrderResponse, dependencies=[Depends(get_current_admin)])
async def admin_update_order(order_id: str, payload: OrderStatusUpdate) -> dict:
    return await OrderService.update_order_status(order_id, payload.status)
