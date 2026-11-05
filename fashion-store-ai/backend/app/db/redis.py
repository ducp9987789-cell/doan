from __future__ import annotations

import logging
from typing import Optional

from redis.asyncio import Redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_redis: Optional[Redis] = None


async def connect_to_redis() -> Optional[Redis]:
    """Connect to Redis. Returns None when Redis is unavailable (local fallback)."""
    global _redis
    settings = get_settings()
    client = Redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )
    try:
        await client.ping()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Redis unavailable (%s). Chat sessions will use in-memory fallback.", exc)
        try:
            await client.aclose()
        except Exception:  # noqa: BLE001
            pass
        _redis = None
        return None
    _redis = client
    logger.info("Connected to Redis at %s", settings.redis_url)
    return _redis


async def close_redis_connection() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
    _redis = None


def get_redis() -> Optional[Redis]:
    return _redis
