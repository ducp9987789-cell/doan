from contextlib import asynccontextmanager
import logging

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import api_router
from app.core.ai_bootstrap import attach_redis_to_ai_core, init_ai_core
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.mongodb import close_mongo_connection, connect_to_mongo
from app.db.redis import close_redis_connection, connect_to_redis, get_redis
from app.services.seed_service import seed_database

setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await connect_to_mongo()
    logger.info("Connected to MongoDB")

    redis_client = await connect_to_redis()
    init_ai_core()
    attach_redis_to_ai_core(redis_client)
    logger.info("AI-core bootstrapped (Qdrant RAG + Redis session/cache)")

    if settings.seed_on_startup:
        result = await seed_database()
        logger.info("Seed completed: %s", result)
    yield

    store = None
    try:
        from bootstrap import get_vector_store_instance

        store = get_vector_store_instance()
        await store.close()
    except Exception:  # noqa: BLE001
        pass

    await close_redis_connection()
    await close_mongo_connection()
    logger.info("Connections closed")


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)

# Mount thư mục lưu trữ ảnh tải lên
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="static_uploads")
app.mount("/api/v1/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="api_static_uploads")


@app.get("/health")
async def health() -> dict:
    redis_ok = False
    client = get_redis()
    if client is not None:
        try:
            redis_ok = bool(await client.ping())
        except Exception:  # noqa: BLE001
            redis_ok = False
    return {
        "status": "ok",
        "app": settings.app_name,
        "mongo": True,
        "redis": redis_ok,
        "qdrant_url": settings.qdrant_url,
        "vector_backend": "qdrant",
    }
