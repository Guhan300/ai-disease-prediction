"""Embedding helpers for local RAG."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("rag.embeddings")


@lru_cache(maxsize=1)
def get_embedding_model():
    """Load sentence-transformers model once."""
    from sentence_transformers import SentenceTransformer

    settings = get_settings()
    logger.info("Loading embedding model %s", settings.embedding_model)
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_embedding_model()
    vectors = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return [v.tolist() for v in vectors]
