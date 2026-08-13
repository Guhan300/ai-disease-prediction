"""Singleton registry that loads the trained model once at startup."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("ml.model_registry")


def _resolve(path: str) -> Path:
    p = Path(path)
    if p.is_file():
        return p
    root = Path(__file__).resolve().parents[3]
    return root / path


class ModelRegistry:
    """Holds the loaded sklearn pipeline and metadata."""

    def __init__(self) -> None:
        self.pipeline = None
        self.label_encoder = None
        self.metadata: Dict[str, Any] = {}
        self.load_error: Optional[str] = None

    @property
    def is_ready(self) -> bool:
        return self.pipeline is not None and bool(self.metadata)

    @property
    def feature_names(self) -> List[str]:
        return list(self.metadata.get("features") or [])

    @property
    def class_names(self) -> List[str]:
        if self.label_encoder is not None:
            return [str(c) for c in self.label_encoder.classes_]
        return list(self.metadata.get("classes") or [])

    def load(self) -> bool:
        """Load model artifacts from configured paths. Returns True on success."""
        settings = get_settings()
        try:
            model_path = _resolve(settings.model_path)
            meta_path = _resolve(settings.model_metadata_path)
            if not model_path.is_file():
                self.load_error = (
                    "ML model has not been trained yet. "
                    "Please run: python scripts/train_model.py"
                )
                logger.warning(self.load_error)
                return False
            if not meta_path.is_file():
                self.load_error = f"Model metadata missing at {meta_path}"
                logger.warning(self.load_error)
                return False

            self.pipeline = joblib.load(model_path)
            self.metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            encoder_path = model_path.parent / "label_encoder.joblib"
            if encoder_path.is_file():
                self.label_encoder = joblib.load(encoder_path)
            self.load_error = None
            logger.info(
                "Loaded model '%s' v%s with %s classes",
                self.metadata.get("model_name"),
                self.metadata.get("model_version"),
                len(self.class_names),
            )
            return True
        except Exception as exc:
            self.pipeline = None
            self.metadata = {}
            self.load_error = f"Failed to load model: {exc}"
            logger.exception("Model load failed")
            return False


model_registry = ModelRegistry()
