from datetime import datetime
from typing import Any, Optional

from pymongo import ReturnDocument
from bson import ObjectId
from fastapi import HTTPException, status

from app.core.utils import serialize_doc, slugify, to_object_id
from app.db.mongodb import get_database
from app.schemas.product import (
    CategoryCreate,
    CategoryUpdate,
    ProductCreate,
    ProductUpdate,
    PromotionCreate,
    PromotionUpdate,
)


class ProductService:
    @staticmethod
    async def list_categories(active_only: bool = True) -> list[dict[str, Any]]:
        db = get_database()
        query: dict[str, Any] = {"is_active": True} if active_only else {}
        cursor = db.categories.find(query).sort("name", 1)
        return [serialize_doc(doc) for doc in await cursor.to_list(length=200)]

    @staticmethod
    async def create_category(payload: CategoryCreate) -> dict[str, Any]:
        db = get_database()
        slug = payload.slug or slugify(payload.name)
        existing = await db.categories.find_one({"slug": slug})
        if existing:
            raise HTTPException(status_code=400, detail="Category slug already exists")
        doc = {
            "name": payload.name,
            "slug": slug,
            "description": payload.description,
            "image_url": payload.image_url,
            "is_active": payload.is_active,
            "created_at": datetime.utcnow(),
        }
        result = await db.categories.insert_one(doc)
        doc["_id"] = result.inserted_id
        return serialize_doc(doc)

    @staticmethod
    async def update_category(category_id: str, payload: CategoryUpdate) -> dict[str, Any]:
        db = get_database()
        updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
        if "slug" in updates and updates["slug"]:
            updates["slug"] = slugify(updates["slug"])
        result = await db.categories.find_one_and_update(
            {"_id": to_object_id(category_id)},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )
        if not result:
            raise HTTPException(status_code=404, detail="Category not found")
        return serialize_doc(result)

    @staticmethod
    async def delete_category(category_id: str) -> None:
        db = get_database()
        result = await db.categories.delete_one({"_id": to_object_id(category_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Category not found")

    @staticmethod
    async def list_products(
        *,
        q: Optional[str] = None,
        category_id: Optional[str] = None,
        color: Optional[str] = None,
        size: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        featured: Optional[bool] = None,
        page: int = 1,
        page_size: int = 12,
        active_only: bool = True,
    ) -> dict[str, Any]:
        db = get_database()
        query: dict[str, Any] = {}
        if active_only:
            query["is_active"] = True
        if category_id:
            query["category_id"] = category_id
        if color:
            query["colors"] = {"$regex": f"^{color}$", "$options": "i"}
        if size:
            query["sizes"] = {"$regex": f"^{size}$", "$options": "i"}
        if featured is not None:
            query["is_featured"] = featured
        price_filter: dict[str, Any] = {}
        if min_price is not None:
            price_filter["$gte"] = min_price
        if max_price is not None:
            price_filter["$lte"] = max_price
        if price_filter:
            query["price"] = price_filter
        if q:
            query["$or"] = [
                {"name": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
                {"tags": {"$regex": q, "$options": "i"}},
            ]

        total = await db.products.count_documents(query)
        skip = max(page - 1, 0) * page_size
        cursor = db.products.find(query).sort("created_at", -1).skip(skip).limit(page_size)
        items = [serialize_doc(doc) for doc in await cursor.to_list(length=page_size)]
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    async def get_product(product_id: str) -> dict[str, Any]:
        db = get_database()
        if ObjectId.is_valid(product_id):
            doc = await db.products.find_one({"_id": ObjectId(product_id)})
        else:
            doc = await db.products.find_one({"slug": product_id})
        if not doc:
            raise HTTPException(status_code=404, detail="Product not found")
        return serialize_doc(doc)

    @staticmethod
    async def create_product(payload: ProductCreate) -> dict[str, Any]:
        db = get_database()
        category = await db.categories.find_one({"_id": to_object_id(payload.category_id)})
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
        slug = payload.slug or slugify(payload.name)
        doc = {
            **payload.model_dump(),
            "slug": slug,
            "category_name": category["name"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db.products.insert_one(doc)
        doc["_id"] = result.inserted_id
        return serialize_doc(doc)

    @staticmethod
    async def update_product(product_id: str, payload: ProductUpdate) -> dict[str, Any]:
        db = get_database()
        updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
        if "category_id" in updates:
            category = await db.categories.find_one({"_id": to_object_id(updates["category_id"])})
            if not category:
                raise HTTPException(status_code=400, detail="Category not found")
            updates["category_name"] = category["name"]
        if "slug" in updates and updates["slug"]:
            updates["slug"] = slugify(updates["slug"])
        updates["updated_at"] = datetime.utcnow()
        result = await db.products.find_one_and_update(
            {"_id": to_object_id(product_id)},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
        return serialize_doc(result)

    @staticmethod
    async def delete_product(product_id: str) -> None:
        db = get_database()
        result = await db.products.delete_one({"_id": to_object_id(product_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")

    @staticmethod
    async def list_promotions(active_only: bool = True) -> list[dict[str, Any]]:
        db = get_database()
        query: dict[str, Any] = {"is_active": True} if active_only else {}
        cursor = db.promotions.find(query).sort("created_at", -1)
        return [serialize_doc(doc) for doc in await cursor.to_list(length=100)]

    @staticmethod
    async def create_promotion(payload: PromotionCreate) -> dict[str, Any]:
        db = get_database()
        existing = await db.promotions.find_one({"code": payload.code.upper()})
        if existing:
            raise HTTPException(status_code=400, detail="Promotion code already exists")
        doc = {
            **payload.model_dump(),
            "code": payload.code.upper(),
            "created_at": datetime.utcnow(),
        }
        result = await db.promotions.insert_one(doc)
        doc["_id"] = result.inserted_id
        return serialize_doc(doc)

    @staticmethod
    async def update_promotion(promotion_id: str, payload: PromotionUpdate) -> dict[str, Any]:
        db = get_database()
        updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
        if "code" in updates and updates["code"]:
            updates["code"] = updates["code"].upper()
        result = await db.promotions.find_one_and_update(
            {"_id": to_object_id(promotion_id)},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )
        if not result:
            raise HTTPException(status_code=404, detail="Promotion not found")
        return serialize_doc(result)

    @staticmethod
    async def delete_promotion(promotion_id: str) -> None:
        db = get_database()
        result = await db.promotions.delete_one({"_id": to_object_id(promotion_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Promotion not found")
