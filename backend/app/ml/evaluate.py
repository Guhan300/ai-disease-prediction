"""Evaluation helpers for saved models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split

from app.ml.data_loader import load_dataset, validate_dataset
from app.ml.preprocessing import split_xy
from app.ml.train import evaluate_predictions, resolve_artifact_path


def evaluate_saved_model(
    dataset_path: str,
    target_column: str,
    model_path: str,
    metadata_path: str,
    random_state: int = 42,
) -> Dict[str, Any]:
    """Re-evaluate a saved pipeline on a held-out split and print metrics."""
    meta = json.loads(Path(resolve_artifact_path(metadata_path)).read_text(encoding="utf-8"))
    pipeline = joblib.load(resolve_artifact_path(model_path))
    label_encoder = joblib.load(
        resolve_artifact_path(model_path).parent / "label_encoder.joblib"
    )

    df_raw = load_dataset(dataset_path)
    df, _ = validate_dataset(df_raw, target_column, drop_duplicates=True)
    x, y, _ = split_xy(df, target_column)
    y_encoded = label_encoder.transform(y)

    _, x_test, _, y_test = train_test_split(
        x,
        y_encoded,
        test_size=0.15,
        random_state=random_state,
        stratify=y_encoded,
    )
    y_pred = pipeline.predict(x_test)
    y_proba = pipeline.predict_proba(x_test)
    metrics = evaluate_predictions(
        y_test,
        y_pred,
        y_proba,
        label_names=list(label_encoder.classes_),
    )
    print("=== Saved Model Evaluation ===")
    print(f"Model: {meta.get('model_name')}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Macro F1: {metrics['macro_f1']:.4f}")
    print(f"Weighted F1: {metrics['weighted_f1']:.4f}")
    return metrics
