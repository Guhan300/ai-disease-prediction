"""Ingest local medical documents into FAISS."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.rag.ingest import ingest_knowledge_base  # noqa: E402


def main() -> None:
    result = ingest_knowledge_base()
    print(result)


if __name__ == "__main__":
    main()
