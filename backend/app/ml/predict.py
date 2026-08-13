"""Inference helpers for the trained disease-risk model."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping

import pandas as pd

from app.ml.feature_mapping import conversation_to_feature_frame, humanize_feature
from app.ml.model_registry import ModelRegistry


def predict_top_k(
    extracted_features: Mapping[str, Any],
    registry: ModelRegistry,
    k: int = 3,
) -> Dict[str, Any]:
    """
    Run ML prediction and return top-k condition scores.

    Scores are model-estimated risks, not medically confirmed probabilities.
    """
    if not registry.is_ready:
        raise RuntimeError(
            "ML model has not been trained yet. Please run: python scripts/train_model.py"
        )

    frame = conversation_to_feature_frame(extracted_features, registry.feature_names)
    proba = registry.pipeline.predict_proba(frame)[0]
    classes = registry.class_names

    ranked = sorted(
        (
            {
                "condition": str(classes[i]),
                "score": float(proba[i]),
            }
            for i in range(len(classes))
        ),
        key=lambda item: item["score"],
        reverse=True,
    )[:k]

    present = [
        humanize_feature(col)
        for col in registry.feature_names
        if int(frame.iloc[0][col]) == 1
    ]

    return {
        "top_predictions": ranked,
        "active_features": present,
        "feature_vector": frame.iloc[0].to_dict(),
        "model_name": registry.metadata.get("model_name"),
        "model_version": registry.metadata.get("model_version"),
    }
