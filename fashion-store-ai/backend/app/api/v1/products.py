from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_admin
from app.schemas.product import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
    PromotionCreate,
    PromotionResponse,
    PromotionUpdate,
)
from app.services.product_service import ProductService

router = APIRouter(tags=["products"])


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(active_only: bool = True) -> list[dict]:
    return await ProductService.list_categories(active_only=active_only)


@router.post("/categories", response_model=CategoryResponse, dependencies=[Depends(get_current_admin)])
async def create_category(payload: CategoryCreate) -> dict:
    return await ProductService.create_category(payload)


@router.patch("/categories/{category_id}", response_model=CategoryResponse, dependencies=[Depends(get_current_admin)])
async def update_category(category_id: str, payload: CategoryUpdate) -> dict:
    return await ProductService.update_category(category_id, payload)


@router.delete("/categories/{category_id}", dependencies=[Depends(get_current_admin)])
async def delete_category(category_id: str) -> dict:
    await ProductService.delete_category(category_id)
    return {"message": "Category deleted"}


@router.get("/products", response_model=ProductListResponse)
async def list_products(
    q: Optional[str] = None,
    category_id: Optional[str] = None,
    color: Optional[str] = None,
    size: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    featured: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
) -> dict:
    return await ProductService.list_products(
        q=q,
        category_id=category_id,
        color=color,
        size=size,
        min_price=min_price,
        max_price=max_price,
        featured=featured,
        page=page,
        page_size=page_size,
        active_only=True,
    )


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str) -> dict:
    return await ProductService.get_product(product_id)


@router.post("/products", response_model=ProductResponse, dependencies=[Depends(get_current_admin)])
async def create_product(payload: ProductCreate) -> dict:
    return await ProductService.create_product(payload)


@router.patch("/products/{product_id}", response_model=ProductResponse, dependencies=[Depends(get_current_admin)])
async def update_product(product_id: str, payload: ProductUpdate) -> dict:
    return await ProductService.update_product(product_id, payload)


@router.delete("/products/{product_id}", dependencies=[Depends(get_current_admin)])
async def delete_product(product_id: str) -> dict:
    await ProductService.delete_product(product_id)
    return {"message": "Product deleted"}


@router.get("/promotions", response_model=list[PromotionResponse])
async def list_promotions(active_only: bool = True) -> list[dict]:
    return await ProductService.list_promotions(active_only=active_only)


@router.post("/promotions", response_model=PromotionResponse, dependencies=[Depends(get_current_admin)])
async def create_promotion(payload: PromotionCreate) -> dict:
    return await ProductService.create_promotion(payload)


@router.patch("/promotions/{promotion_id}", response_model=PromotionResponse, dependencies=[Depends(get_current_admin)])
async def update_promotion(promotion_id: str, payload: PromotionUpdate) -> dict:
    return await ProductService.update_promotion(promotion_id, payload)


@router.delete("/promotions/{promotion_id}", dependencies=[Depends(get_current_admin)])
async def delete_promotion(promotion_id: str) -> dict:
    await ProductService.delete_promotion(promotion_id)
    return {"message": "Promotion deleted"}
