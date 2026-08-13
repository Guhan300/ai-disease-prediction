"""FAISS vector store with metadata (Chroma-ready interface)."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

import numpy as np

from app.core.logging import get_logger

logger = get_logger("rag.vector_store")


@dataclass
class ChunkRecord:
    chunk_id: str
    text: str
    source: str
    document: str
    section: str


class VectorStore(Protocol):
    def add(self, embeddings: List[List[float]], records: List[ChunkRecord]) -> None: ...
    def search(self, query_embedding: List[float], top_k: int = 4) -> List[Dict[str, Any]]: ...
    def save(self, path: Path) -> None: ...
    def load(self, path: Path) -> None: ...


class FaissVectorStore:
    """Simple FAISS IndexFlatIP store with parallel metadata JSON."""

    def __init__(self) -> None:
        self.index = None
        self.records: List[ChunkRecord] = []
        self.dim: Optional[int] = None

    def add(self, embeddings: List[List[float]], records: List[ChunkRecord]) -> None:
        import faiss

        if not embeddings:
            return
        matrix = np.asarray(embeddings, dtype="float32")
        if self.index is None:
            self.dim = matrix.shape[1]
            self.index = faiss.IndexFlatIP(self.dim)
        self.index.add(matrix)
        self.records.extend(records)

    def search(self, query_embedding: List[float], top_k: int = 4) -> List[Dict[str, Any]]:
        if self.index is None or not self.records:
            return []
        import faiss

        query = np.asarray([query_embedding], dtype="float32")
        scores, indices = self.index.search(query, min(top_k, len(self.records)))
        results: List[Dict[str, Any]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            record = self.records[idx]
            results.append(
                {
                    **asdict(record),
                    "score": float(score),
                }
            )
        return results

    def save(self, path: Path) -> None:
        import faiss

        path.mkdir(parents=True, exist_ok=True)
        if self.index is not None:
            faiss.write_index(self.index, str(path / "index.faiss"))
        meta = [asdict(r) for r in self.records]
        (path / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    def load(self, path: Path) -> None:
        import faiss

        index_file = path / "index.faiss"
        meta_file = path / "metadata.json"
        if not index_file.is_file() or not meta_file.is_file():
            raise FileNotFoundError(f"FAISS index not found at {path}")
        self.index = faiss.read_index(str(index_file))
        raw = json.loads(meta_file.read_text(encoding="utf-8"))
        self.records = [ChunkRecord(**item) for item in raw]
        self.dim = self.index.d if self.index is not None else None
