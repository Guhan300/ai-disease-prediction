"""Evaluate the saved MedAI model."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import get_settings  # noqa: E402
from app.ml.evaluate import evaluate_saved_model  # noqa: E402


def main() -> None:
    settings = get_settings()
    evaluate_saved_model(
        dataset_path=settings.dataset_path,
        target_column=settings.target_column,
        model_path=settings.model_path,
        metadata_path=settings.model_metadata_path,
    )


if __name__ == "__main__":
    main()
