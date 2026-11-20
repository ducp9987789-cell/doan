from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from pymongo import ReturnDocument

from app.core.security import get_current_admin, hash_password
from app.core.utils import serialize_doc, to_object_id
from app.db.mongodb import get_database
from app.schemas.user import UserResponse
from app.services.order_service import OrderService
from app.services.product_service import ProductService

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_admin)])

PENDING_STATUSES = {"pending", "confirmed"}


class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str
    phone: Optional[str] = None
    role: str = "customer"
    is_active: bool = True


class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=6)


def _parse_day(value: Optional[str], fallback: datetime) -> datetime:
    if not value:
        return fallback
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD") from exc


def _order_day(order: dict) -> Optional[str]:
    created = order.get("created_at")
    if not created:
        return None
    if isinstance(created, str):
        try:
            created = datetime.fromisoformat(created.replace("Z", "+00:00"))
        except ValueError:
            return None
    return created.strftime("%Y-%m-%d")


def _build_daily_series(orders: list[dict], start: datetime, end: datetime) -> dict:
    days: list[str] = []
    cursor = start.date()
    end_day = end.date()
    while cursor <= end_day:
        days.append(cursor.strftime("%Y-%m-%d"))
        cursor += timedelta(days=1)

    revenue_map = {day: 0.0 for day in days}
    order_map = {day: 0 for day in days}
    for order in orders:
        day = _order_day(order)
        if not day or day not in order_map:
            continue
        order_map[day] += 1
        if order.get("status") != "cancelled":
            revenue_map[day] += float(order.get("total") or 0)

    return {
        "labels": days,
        "revenue": [round(revenue_map[day], 0) for day in days],
        "orders": [order_map[day] for day in days],
    }


@router.get("/dashboard")
async def dashboard(
    chart_from: Optional[str] = Query(default=None),
    chart_to: Optional[str] = Query(default=None),
) -> dict:
    db = get_database()
    orders = await OrderService.list_orders()

    today = datetime.utcnow().date()
    pending_orders = [o for o in orders if o.get("status") in PENDING_STATUSES]
    today_pending = [
        o
        for o in pending_orders
        if _order_day(o) == today.strftime("%Y-%m-%d")
    ]

    revenue = sum(
        float(order.get("total") or 0)
        for order in orders
        if order.get("status") == "completed"
    )

    end_dt = _parse_day(chart_to, datetime.utcnow())
    start_dt = _parse_day(chart_from, end_dt - timedelta(days=6))
    if start_dt > end_dt:
        start_dt, end_dt = end_dt, start_dt

    charts = _build_daily_series(orders, start_dt, end_dt)

    return {
        "users": await db.users.count_documents({}),
        "products": await db.products.count_documents({}),
        "orders": await db.orders.count_documents({}),
        "pending_orders": len(pending_orders),
        "today_pending_orders": len(today_pending),
        "promotions": await db.promotions.count_documents({"is_active": True}),
        "chat_logs": await db.chat_logs.count_documents({}),
        "revenue": revenue,
        "recent_orders": orders[:5],
        "pending_order_list": today_pending[:50] or pending_orders[:20],
        "charts": charts,
        "chart_from": start_dt.strftime("%Y-%m-%d"),
        "chart_to": end_dt.strftime("%Y-%m-%d"),
        "featured_products": (
            await ProductService.list_products(featured=True, page=1, page_size=5, active_only=False)
        )["items"],
    }


@router.get("/users", response_model=list[UserResponse])
async def list_users() -> list[dict]:
    db = get_database()
    cursor = db.users.find({}).sort("created_at", -1)
    return [serialize_doc(doc) for doc in await cursor.to_list(length=500)]


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: AdminUserCreate) -> dict:
    if payload.role not in {"customer", "admin"}:
        raise HTTPException(status_code=400, detail="Invalid role")
    db = get_database()
    existing = await db.users.find_one({"email": payload.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    doc = {
        "email": payload.email.lower(),
        "full_name": payload.full_name,
        "hashed_password": hash_password(payload.password),
        "role": payload.role,
        "phone": payload.phone,
        "address": None,
        "is_active": payload.is_active,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db.users.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, payload: AdminUserUpdate, current_admin: dict = Depends(get_current_admin)) -> dict:
    if payload.role is not None and payload.role not in {"customer", "admin"}:
        raise HTTPException(status_code=400, detail="Invalid role")

    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if k != "password"}
    if payload.password:
        updates["hashed_password"] = hash_password(payload.password)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Prevent admin from locking themselves out
    if str(current_admin.get("id")) == str(user_id):
        if updates.get("is_active") is False:
            raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
        if updates.get("role") == "customer":
            raise HTTPException(status_code=400, detail="Cannot remove admin role from your own account")

    updates["updated_at"] = datetime.utcnow()
    db = get_database()
    result = await db.users.find_one_and_update(
        {"_id": to_object_id(user_id)},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_doc(result)


@router.get("/products")
async def admin_products(page: int = 1, page_size: int = 50) -> dict:
    return await ProductService.list_products(page=page, page_size=page_size, active_only=False)
