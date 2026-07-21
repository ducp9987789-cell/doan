from fastapi import APIRouter, Depends

from app.core.security import get_current_admin
from app.core.utils import serialize_doc
from app.db.mongodb import get_database
from app.schemas.user import UserResponse
from app.services.order_service import OrderService
from app.services.product_service import ProductService

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_admin)])


@router.get("/dashboard")
async def dashboard() -> dict:
    db = get_database()
    orders = await OrderService.list_orders()
    revenue = sum(order.get("total", 0) for order in orders if order.get("status") != "cancelled")
    return {
        "users": await db.users.count_documents({}),
        "products": await db.products.count_documents({}),
        "orders": await db.orders.count_documents({}),
        "promotions": await db.promotions.count_documents({"is_active": True}),
        "chat_logs": await db.chat_logs.count_documents({}),
        "revenue": revenue,
        "recent_orders": orders[:5],
        "featured_products": (
            await ProductService.list_products(featured=True, page=1, page_size=5, active_only=False)
        )["items"],
    }


@router.get("/users", response_model=list[UserResponse])
async def list_users() -> list[dict]:
    db = get_database()
    cursor = db.users.find({}).sort("created_at", -1)
    return [serialize_doc(doc) for doc in await cursor.to_list(length=200)]


@router.get("/products")
async def admin_products(page: int = 1, page_size: int = 50) -> dict:
    return await ProductService.list_products(page=page, page_size=page_size, active_only=False)
