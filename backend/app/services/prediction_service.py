"""Prediction service wrapping ML + SHAP."""

from __future__ import annotations

from typing import Any, Dict, Mapping

from app.ml.explain import explain_prediction
from app.ml.model_registry import ModelRegistry, model_registry
from app.ml.predict import predict_top_k


class PredictionService:
    def __init__(self, registry: ModelRegistry | None = None) -> None:
        self.registry = registry or model_registry

    def predict(self, features: Mapping[str, Any]) -> Dict[str, Any]:
        result = predict_top_k(features, self.registry, k=3)
        top = result["top_predictions"][0]["condition"] if result["top_predictions"] else None
        explanation = explain_prediction(features, self.registry, predicted_class=top)
        return {
            **result,
            "explanation": explanation,
        }


prediction_service = PredictionService()
