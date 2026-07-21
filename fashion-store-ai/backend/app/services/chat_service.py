from datetime import datetime
from typing import Any, Optional

from pymongo import ReturnDocument
from fastapi import HTTPException

from app.core.utils import new_session_id, serialize_doc, to_object_id
from app.db.mongodb import get_database
from app.schemas.chat import ChatRequest, FAQCreate, FAQUpdate, StoreInfoUpdate


class ChatService:
    @staticmethod
    async def ask(payload: ChatRequest, user_id: Optional[str] = None) -> dict[str, Any]:
        from bootstrap import get_shopping_agent

        session_id = payload.session_id or new_session_id()
        agent = get_shopping_agent()
        result = await agent.run(payload.message, session_id=session_id)

        db = get_database()
        await db.chat_logs.insert_one(
            {
                "user_id": user_id,
                "session_id": session_id,
                "question": payload.message,
                "answer": result.answer,
                "sources": result.sources,
                "created_at": datetime.utcnow(),
            }
        )
        return {
            "session_id": session_id,
            "answer": result.answer,
            "sources": result.sources,
            "suggested_products": result.suggested_products,
        }

    @staticmethod
    async def list_faqs(active_only: bool = True) -> list[dict[str, Any]]:
        db = get_database()
        query: dict[str, Any] = {"is_active": True} if active_only else {}
        cursor = db.faqs.find(query).sort("created_at", -1)
        return [serialize_doc(doc) for doc in await cursor.to_list(length=200)]

    @staticmethod
    async def create_faq(payload: FAQCreate) -> dict[str, Any]:
        db = get_database()
        doc = {**payload.model_dump(), "created_at": datetime.utcnow()}
        result = await db.faqs.insert_one(doc)
        doc["_id"] = result.inserted_id
        await ChatService.reindex_knowledge()
        return serialize_doc(doc)

    @staticmethod
    async def update_faq(faq_id: str, payload: FAQUpdate) -> dict[str, Any]:
        db = get_database()
        updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
        result = await db.faqs.find_one_and_update(
            {"_id": to_object_id(faq_id)},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )
        if not result:
            raise HTTPException(status_code=404, detail="FAQ not found")
        await ChatService.reindex_knowledge()
        return serialize_doc(result)

    @staticmethod
    async def delete_faq(faq_id: str) -> None:
        db = get_database()
        result = await db.faqs.delete_one({"_id": to_object_id(faq_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="FAQ not found")
        await ChatService.reindex_knowledge()

    @staticmethod
    async def get_store_info() -> dict[str, Any]:
        db = get_database()
        info = await db.store_info.find_one({})
        if not info:
            raise HTTPException(status_code=404, detail="Store info not found")
        info.pop("_id", None)
        return info

    @staticmethod
    async def update_store_info(payload: StoreInfoUpdate) -> dict[str, Any]:
        db = get_database()
        updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
        updates["updated_at"] = datetime.utcnow()
        await db.store_info.update_one({}, {"$set": updates}, upsert=True)
        await ChatService.reindex_knowledge()
        return await ChatService.get_store_info()

    @staticmethod
    async def list_chat_logs(limit: int = 100) -> list[dict[str, Any]]:
        db = get_database()
        cursor = db.chat_logs.find({}).sort("created_at", -1).limit(limit)
        return [serialize_doc(doc) for doc in await cursor.to_list(length=limit)]

    @staticmethod
    async def reindex_knowledge() -> int:
        from bootstrap import get_knowledge_indexer

        indexer = get_knowledge_indexer()
        return await indexer.run()
