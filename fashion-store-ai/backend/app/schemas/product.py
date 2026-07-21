from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str
    slug: Optional[str] = None
    description: str = ""
    image_url: str = ""
    is_active: bool = True


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str = ""
    image_url: str = ""
    is_active: bool = True


class ProductVariantSchema(BaseModel):
    color: str
    size: str
    stock: int = 0
    sku: Optional[str] = None


class ProductCreate(BaseModel):
    name: str
    slug: Optional[str] = None
    description: str
    price: float
    sale_price: Optional[float] = None
    category_id: str
    images: list[str] = Field(default_factory=list)
    colors: list[str] = Field(default_factory=list)
    sizes: list[str] = Field(default_factory=list)
    variants: list[ProductVariantSchema] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    stock: int = 0
    is_featured: bool = False
    is_active: bool = True


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    sale_price: Optional[float] = None
    category_id: Optional[str] = None
    images: Optional[list[str]] = None
    colors: Optional[list[str]] = None
    sizes: Optional[list[str]] = None
    variants: Optional[list[ProductVariantSchema]] = None
    tags: Optional[list[str]] = None
    stock: Optional[int] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    price: float
    sale_price: Optional[float] = None
    category_id: str
    category_name: str = ""
    images: list[str] = Field(default_factory=list)
    colors: list[str] = Field(default_factory=list)
    sizes: list[str] = Field(default_factory=list)
    variants: list[ProductVariantSchema] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    stock: int = 0
    is_featured: bool = False
    is_active: bool = True
    created_at: Optional[datetime] = None


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int


class PromotionCreate(BaseModel):
    code: str
    title: str
    description: str = ""
    discount_type: str = "percent"
    discount_value: float
    min_order_value: float = 0
    is_active: bool = True
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None


class PromotionUpdate(BaseModel):
    code: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None
    min_order_value: Optional[float] = None
    is_active: Optional[bool] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None


class PromotionResponse(BaseModel):
    id: str
    code: str
    title: str
    description: str = ""
    discount_type: str
    discount_value: float
    min_order_value: float = 0
    is_active: bool = True
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
