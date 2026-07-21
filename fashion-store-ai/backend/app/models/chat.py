from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ChatLogInDB(BaseModel):
    user_id: Optional[str] = None
    session_id: str
    question: str
    answer: str
    sources: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FAQInDB(BaseModel):
    question: str
    answer: str
    category: str = "general"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StoreInfoInDB(BaseModel):
    store_name: str
    hotline: str
    email: str
    address: str
    shipping_policy: str
    return_policy: str
    about: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)
