"""Train MedAI disease-risk models from DATASET_PATH."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import get_settings  # noqa: E402
from app.ml.train import train_and_select  # noqa: E402


def main() -> None:
    settings = get_settings()
    train_and_select(
        dataset_path=settings.dataset_path,
        target_column=settings.target_column,
        primary_metric=settings.primary_metric,
        model_path=settings.model_path,
        preprocessor_path=settings.preprocessor_path,
        metadata_path=settings.model_metadata_path,
    )


if __name__ == "__main__":
    main()
