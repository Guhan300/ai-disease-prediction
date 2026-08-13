"""SHAP-based explainability helpers."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

import numpy as np
import pandas as pd

from app.core.logging import get_logger
from app.ml.feature_mapping import conversation_to_feature_frame, humanize_feature
from app.ml.model_registry import ModelRegistry

logger = get_logger("ml.explain")


def _impact_label(value: float, max_abs: float) -> str:
    if max_abs <= 0:
        return "low"
    ratio = abs(value) / max_abs
    if ratio >= 0.66:
        return "high"
    if ratio >= 0.33:
        return "medium"
    return "low"


def explain_prediction(
    extracted_features: Mapping[str, Any],
    registry: ModelRegistry,
    predicted_class: Optional[str] = None,
    top_n: int = 6,
) -> Dict[str, Any]:
    """
    Return user-friendly feature contributions for the predicted class.

    Falls back to active-feature listing if SHAP is unavailable.
    """
    if not registry.is_ready:
        return {"important_features": [], "method": "unavailable"}

    frame = conversation_to_feature_frame(extracted_features, registry.feature_names)
    class_names = list(registry.class_names)
    if predicted_class is None:
        pred_idx = int(registry.pipeline.predict(frame)[0])
        predicted_class = str(class_names[pred_idx])
    else:
        pred_idx = class_names.index(predicted_class) if predicted_class in class_names else 0

    try:
        import shap

        model = registry.pipeline.named_steps["model"]
        pre = registry.pipeline.named_steps["preprocessor"]
        transformed = pre.transform(frame)

        # Prefer TreeExplainer for tree models; Kernel as fallback is too slow.
        explainer = None
        values = None
        if hasattr(model, "feature_importances_") or model.__class__.__name__ in {
            "XGBClassifier",
            "RandomForestClassifier",
        }:
            explainer = shap.TreeExplainer(model)
            values = explainer.shap_values(transformed)
        elif hasattr(model, "coef_"):
            # Linear model coefficients * scaled features as contribution proxy
            coef = np.asarray(model.coef_)
            if coef.ndim == 1:
                contrib = coef * transformed[0]
            else:
                contrib = coef[pred_idx] * transformed[0]
            pairs = list(zip(registry.feature_names, contrib))
            pairs.sort(key=lambda x: abs(x[1]), reverse=True)
            max_abs = max((abs(v) for _, v in pairs), default=0.0)
            important = [
                {
                    "feature": humanize_feature(name),
                    "impact": _impact_label(float(val), float(max_abs)),
                    "direction": "increases" if val >= 0 else "decreases",
                }
                for name, val in pairs[:top_n]
                if abs(val) > 1e-9
            ]
            return {
                "important_features": important,
                "method": "linear_coefficients",
                "predicted_class": predicted_class,
            }
        else:
            # Generic: use feature presence ranked by class probability sensitivity
            raise RuntimeError("No fast explainer for this model type")

        if isinstance(values, list):
            class_values = np.asarray(values[pred_idx])[0]
        else:
            arr = np.asarray(values)
            if arr.ndim == 3:
                class_values = arr[0, :, pred_idx]
            else:
                class_values = arr[0]

        pairs = list(zip(registry.feature_names, class_values))
        pairs.sort(key=lambda x: abs(x[1]), reverse=True)
        max_abs = max((abs(v) for _, v in pairs), default=0.0)
        important = [
            {
                "feature": humanize_feature(name),
                "impact": _impact_label(float(val), float(max_abs)),
                "direction": "increases" if val >= 0 else "decreases",
            }
            for name, val in pairs[:top_n]
            if abs(val) > 1e-9
        ]
        return {
            "important_features": important,
            "method": "shap",
            "predicted_class": predicted_class,
        }
    except Exception as exc:
        logger.warning("SHAP explanation fallback: %s", exc)
        active = [
            {
                "feature": humanize_feature(col),
                "impact": "high" if int(frame.iloc[0][col]) == 1 else "low",
                "direction": "increases",
            }
            for col in registry.feature_names
            if int(frame.iloc[0][col]) == 1
        ][:top_n]
        return {
            "important_features": active,
            "method": "active_features_fallback",
            "predicted_class": predicted_class,
        }
