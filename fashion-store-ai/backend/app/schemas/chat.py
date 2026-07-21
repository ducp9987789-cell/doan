from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: Optional[str] = None


class SuggestedProduct(BaseModel):
    id: str
    name: str
    price: float
    sale_price: Optional[float] = None
    image: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[dict[str, Any]] = Field(default_factory=list)
    suggested_products: list[SuggestedProduct] = Field(default_factory=list)


class FAQCreate(BaseModel):
    question: str
    answer: str
    category: str = "general"
    is_active: bool = True


class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class FAQResponse(BaseModel):
    id: str
    question: str
    answer: str
    category: str
    is_active: bool


class StoreInfoUpdate(BaseModel):
    store_name: Optional[str] = None
    hotline: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    shipping_policy: Optional[str] = None
    return_policy: Optional[str] = None
    about: Optional[str] = None


class StoreInfoResponse(BaseModel):
    store_name: str
    hotline: str
    email: str
    address: str
    shipping_policy: str
    return_policy: str
    about: str
    updated_at: Optional[datetime] = None


class ChatLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    session_id: str
    question: str
    answer: str
    created_at: Optional[datetime] = None
