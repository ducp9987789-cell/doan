from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CartItem(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int
    color: Optional[str] = None
    size: Optional[str] = None
    image: Optional[str] = None


class CartInDB(BaseModel):
    user_id: str
    items: list[CartItem] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OrderItem(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int
    color: Optional[str] = None
    size: Optional[str] = None
    image: Optional[str] = None


class ShippingAddress(BaseModel):
    full_name: str
    phone: str
    address: str
    city: str
    district: Optional[str] = None
    note: Optional[str] = None


class OrderInDB(BaseModel):
    user_id: str
    items: list[OrderItem]
    shipping_address: ShippingAddress
    payment_method: str = "cod"
    status: str = "pending"
    subtotal: float
    discount: float = 0
    shipping_fee: float = 0
    total: float
    promotion_code: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
