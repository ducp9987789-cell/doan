from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo() -> None:
    global _client, _db
    settings = get_settings()
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    _db = _client[settings.mongodb_db]
    await _db.command("ping")
    await _ensure_indexes(_db)


async def close_mongo_connection() -> None:
    global _client, _db
    if _client:
        _client.close()
    _client = None
    _db = None


def get_database() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("MongoDB is not connected")
    return _db


async def _ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    await db.users.create_index("email", unique=True)
    await db.products.create_index([("name", "text"), ("description", "text"), ("tags", "text")])
    await db.products.create_index("category_id")
    await db.categories.create_index("slug", unique=True)
    await db.orders.create_index("user_id")
    await db.carts.create_index("user_id", unique=True)
    await db.promotions.create_index("code", unique=True)
    await db.chat_logs.create_index("created_at")
