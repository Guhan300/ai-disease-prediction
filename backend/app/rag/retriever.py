"""Retriever over the local FAISS index."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.core.logging import get_logger
from app.rag.embeddings import embed_texts
from app.rag.vector_store import FaissVectorStore

logger = get_logger("rag.retriever")


class MedicalRetriever:
    def __init__(self) -> None:
        self.store = FaissVectorStore()
        self.loaded = False
        self.error: Optional[str] = None

    def load(self) -> bool:
        settings = get_settings()
        path = Path(settings.vector_store_path)
        if not path.is_absolute():
            path = Path(__file__).resolve().parents[3] / path
        try:
            self.store.load(path)
            self.loaded = True
            self.error = None
            logger.info("Loaded FAISS index from %s", path)
            return True
        except Exception as exc:
            self.loaded = False
            self.error = str(exc)
            logger.warning("FAISS index unavailable: %s", exc)
            return False

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        if not self.loaded:
            return []
        try:
            vector = embed_texts([query])[0]
            return self.store.search(vector, top_k=top_k)
        except Exception as exc:
            logger.warning("RAG search failed: %s", exc)
            return []

    def list_sources(self) -> List[str]:
        if not self.loaded:
            return []
        return sorted({r.source for r in self.store.records})


retriever = MedicalRetriever()
