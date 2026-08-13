"""Knowledge-base ingestion for local RAG."""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Iterable, List, Tuple

from app.core.config import get_settings
from app.core.logging import get_logger
from app.rag.embeddings import embed_texts
from app.rag.vector_store import ChunkRecord, FaissVectorStore

logger = get_logger("rag.ingest")


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def resolve_path(path: str | Path) -> Path:
    p = Path(path)
    if p.exists():
        return p
    return _project_root() / path


def read_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts)
    raise ValueError(f"Unsupported document type: {path}")


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 700, overlap: int = 120) -> List[Tuple[str, str]]:
    """Split text into overlapping chunks; return (section, chunk)."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[Tuple[str, str]] = []
    buffer = ""
    section = "general"
    for para in paragraphs:
        if len(para) < 80 and para.endswith(":"):
            section = para.rstrip(":")
        candidate = f"{buffer}\n\n{para}".strip() if buffer else para
        if len(candidate) <= chunk_size:
            buffer = candidate
            continue
        if buffer:
            chunks.append((section, buffer))
        if len(para) <= chunk_size:
            buffer = para
        else:
            start = 0
            while start < len(para):
                end = min(len(para), start + chunk_size)
                chunks.append((section, para[start:end]))
                start = max(end - overlap, end)
            buffer = ""
    if buffer:
        chunks.append((section, buffer))
    return chunks


def ingest_knowledge_base(
    docs_path: str | None = None,
    store_path: str | None = None,
) -> dict:
    settings = get_settings()
    source_dir = resolve_path(docs_path or settings.knowledge_base_path)
    out_dir = resolve_path(store_path or settings.vector_store_path)
    source_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(
        [
            p
            for p in source_dir.rglob("*")
            if p.suffix.lower() in {".txt", ".md", ".pdf"} and p.is_file()
        ]
    )
    if not files:
        raise FileNotFoundError(
            f"No documents found in {source_dir}. Add .txt/.md/.pdf files first."
        )

    store = FaissVectorStore()
    all_texts: List[str] = []
    all_records: List[ChunkRecord] = []

    for path in files:
        text = clean_text(read_document(path))
        for section, chunk in chunk_text(text):
            record = ChunkRecord(
                chunk_id=str(uuid.uuid4()),
                text=chunk,
                source=str(path.name),
                document=path.stem,
                section=section,
            )
            all_texts.append(chunk)
            all_records.append(record)

    embeddings = embed_texts(all_texts)
    store.add(embeddings, all_records)
    store.save(out_dir)
    logger.info("Ingested %s chunks from %s docs → %s", len(all_records), len(files), out_dir)
    return {
        "documents": len(files),
        "chunks": len(all_records),
        "store_path": str(out_dir),
    }
