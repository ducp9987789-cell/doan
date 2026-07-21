from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryInDB(BaseModel):
    name: str
    slug: str
    description: str = ""
    image_url: str = ""
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProductVariant(BaseModel):
    color: str
    size: str
    stock: int = 0
    sku: Optional[str] = None


class ProductInDB(BaseModel):
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
    variants: list[ProductVariant] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    stock: int = 0
    is_featured: bool = False
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PromotionInDB(BaseModel):
    code: str
    title: str
    description: str = ""
    discount_type: str = "percent"
    discount_value: float
    min_order_value: float = 0
    is_active: bool = True
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
