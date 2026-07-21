from fastapi import APIRouter, Depends

from app.core.security import get_current_admin, get_optional_user
from app.schemas.chat import (
    ChatLogResponse,
    ChatRequest,
    ChatResponse,
    FAQCreate,
    FAQResponse,
    FAQUpdate,
    StoreInfoResponse,
    StoreInfoUpdate,
)
from app.services.chat_service import ChatService

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, current_user: dict | None = Depends(get_optional_user)) -> dict:
    user_id = current_user["id"] if current_user else None
    return await ChatService.ask(payload, user_id=user_id)


@router.get("/faqs", response_model=list[FAQResponse])
async def list_faqs() -> list[dict]:
    return await ChatService.list_faqs(active_only=True)


@router.post("/faqs", response_model=FAQResponse, dependencies=[Depends(get_current_admin)])
async def create_faq(payload: FAQCreate) -> dict:
    return await ChatService.create_faq(payload)


@router.patch("/faqs/{faq_id}", response_model=FAQResponse, dependencies=[Depends(get_current_admin)])
async def update_faq(faq_id: str, payload: FAQUpdate) -> dict:
    return await ChatService.update_faq(faq_id, payload)


@router.delete("/faqs/{faq_id}", dependencies=[Depends(get_current_admin)])
async def delete_faq(faq_id: str) -> dict:
    await ChatService.delete_faq(faq_id)
    return {"message": "FAQ deleted"}


@router.get("/store-info", response_model=StoreInfoResponse)
async def get_store_info() -> dict:
    return await ChatService.get_store_info()


@router.put("/store-info", response_model=StoreInfoResponse, dependencies=[Depends(get_current_admin)])
async def update_store_info(payload: StoreInfoUpdate) -> dict:
    return await ChatService.update_store_info(payload)


@router.get("/admin/chat-logs", response_model=list[ChatLogResponse], dependencies=[Depends(get_current_admin)])
async def list_chat_logs() -> list[dict]:
    return await ChatService.list_chat_logs()


@router.post("/admin/reindex", dependencies=[Depends(get_current_admin)])
async def reindex_knowledge() -> dict:
    count = await ChatService.reindex_knowledge()
    return {"indexed_documents": count}
