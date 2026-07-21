from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(ge=1, default=1)
    color: Optional[str] = None
    size: Optional[str] = None


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=0)


class CartItemResponse(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int
    color: Optional[str] = None
    size: Optional[str] = None
    image: Optional[str] = None


class CartResponse(BaseModel):
    user_id: str
    items: list[CartItemResponse]
    subtotal: float
    item_count: int


class ShippingAddressSchema(BaseModel):
    full_name: str
    phone: str
    address: str
    city: str
    district: Optional[str] = None
    note: Optional[str] = None


class OrderCreate(BaseModel):
    shipping_address: ShippingAddressSchema
    payment_method: str = "cod"
    promotion_code: Optional[str] = None


class OrderItemResponse(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int
    color: Optional[str] = None
    size: Optional[str] = None
    image: Optional[str] = None


class OrderResponse(BaseModel):
    id: str
    user_id: str
    items: list[OrderItemResponse]
    shipping_address: ShippingAddressSchema
    payment_method: str
    status: str
    subtotal: float
    discount: float
    shipping_fee: float
    total: float
    promotion_code: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OrderStatusUpdate(BaseModel):
    status: str
