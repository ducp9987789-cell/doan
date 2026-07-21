from __future__ import annotations

import sys
from pathlib import Path


def ensure_ai_core_on_path() -> Path:
    """Add backend/ai-core to sys.path so packages like llm/memory/tool import cleanly."""
    backend_dir = Path(__file__).resolve().parents[2]
    ai_core_dir = backend_dir / "ai-core"
    ai_core_str = str(ai_core_dir)
    if ai_core_str not in sys.path:
        sys.path.insert(0, ai_core_str)
    return ai_core_dir


def init_ai_core() -> None:
    ensure_ai_core_on_path()

    from app.core.config import get_settings
    from app.db.mongodb import get_database
    from bootstrap import bootstrap_ai_core
    from tool.document_loader import build_knowledge_documents

    settings = get_settings()

    async def document_loader():
        return await build_knowledge_documents(get_database())

    bootstrap_ai_core(
        chroma_persist_dir=settings.chroma_persist_dir,
        llm_provider=settings.llm_provider,
        openai_api_key=settings.openai_api_key,
        openai_model=settings.openai_model,
        openai_embedding_model=settings.openai_embedding_model,
        gemini_api_key=settings.gemini_api_key,
        gemini_model=settings.gemini_model,
        db_getter=get_database,
        document_loader=document_loader,
    )
