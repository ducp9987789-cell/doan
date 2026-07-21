from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.ai_bootstrap import init_ai_core
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.mongodb import close_mongo_connection, connect_to_mongo
from app.services.seed_service import seed_database

setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await connect_to_mongo()
    logger.info("Connected to MongoDB")
    init_ai_core()
    logger.info("AI-core bootstrapped")
    if settings.seed_on_startup:
        result = await seed_database()
        logger.info("Seed completed: %s", result)
    yield
    await close_mongo_connection()
    logger.info("MongoDB connection closed")


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "app": settings.app_name}
