from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Fashion Store AI"
    app_env: str = "development"
    secret_key: str = "dev-secret-key"
    access_token_expire_minutes: int = 1440
    algorithm: str = "HS256"

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "fashion_store"

    redis_url: str = "redis://localhost:6379/0"
    redis_session_ttl_seconds: int = 86400
    redis_rag_cache_ttl_seconds: int = 300

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "fashion_knowledge"

    # Kept for backward compatibility with older .env files; unused by Qdrant path.
    chroma_persist_dir: str = "./data/chroma"

    llm_provider: str = "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    admin_email: str = "admin@fashionstore.local"
    admin_password: str = "Admin@123"
    seed_on_startup: bool = True

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
