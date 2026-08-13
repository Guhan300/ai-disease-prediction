"""Model training, comparison, and artifact persistence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from xgboost import XGBClassifier

from app.core.logging import get_logger
from app.ml.data_loader import load_dataset, print_report, validate_dataset
from app.ml.preprocessing import build_label_encoder, build_preprocessor, split_xy

logger = get_logger("ml.train")

METRIC_KEYS = {
    "accuracy": "accuracy",
    "macro_f1": "macro_f1",
    "weighted_f1": "weighted_f1",
}


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def resolve_artifact_path(path: str | Path) -> Path:
    p = Path(path)
    if p.is_absolute():
        return p
    return _project_root() / p


def build_candidate_models(random_state: int = 42) -> Dict[str, Any]:
    """Create candidate estimators (unfitted)."""
    return {
        "logistic_regression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=random_state,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            class_weight="balanced_subsample",
            random_state=random_state,
            n_jobs=-1,
        ),
        "xgboost": XGBClassifier(
            n_estimators=200,
            learning_rate=0.08,
            max_depth=5,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="multi:softprob",
            eval_metric="mlogloss",
            random_state=random_state,
            n_jobs=-1,
        ),
        "svm": CalibratedClassifierCV(
            LinearSVC(class_weight="balanced", random_state=random_state, max_iter=5000),
            method="sigmoid",
            cv=3,
        ),
    }


def _safe_roc_auc(y_true, y_proba, labels) -> Optional[float]:
    try:
        if y_proba.ndim == 1 or y_proba.shape[1] < 2:
            return None
        return float(
            roc_auc_score(
                y_true,
                y_proba,
                multi_class="ovr",
                average="weighted",
                labels=labels,
            )
        )
    except Exception:
        return None


def evaluate_predictions(
    y_true,
    y_pred,
    y_proba,
    label_names: List[str],
) -> Dict[str, Any]:
    """Compute classification metrics for model comparison."""
    labels = list(range(len(label_names)))
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(
            precision_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "recall_macro": float(
            recall_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "weighted_f1": float(
            f1_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "roc_auc_weighted_ovr": _safe_roc_auc(y_true, y_proba, labels),
        "classification_report": classification_report(
            y_true,
            y_pred,
            target_names=label_names,
            zero_division=0,
            output_dict=True,
        ),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }
    return metrics


def train_and_select(
    dataset_path: str,
    target_column: str,
    primary_metric: str = "macro_f1",
    model_path: str = "backend/models/trained/best_model.joblib",
    preprocessor_path: str = "backend/models/trained/preprocessor.joblib",
    metadata_path: str = "backend/models/metadata/model_metadata.json",
    random_state: int = 42,
) -> Dict[str, Any]:
    """Full training pipeline: load → validate → train → compare → save best."""
    df_raw = load_dataset(dataset_path)
    df, report = validate_dataset(df_raw, target_column, drop_duplicates=True)
    report.path = str(resolve_artifact_path(dataset_path))
    print_report(report)

    x, y, feature_columns = split_xy(df, target_column)
    label_encoder = build_label_encoder(y)
    y_encoded = label_encoder.transform(y)

    x_train, x_temp, y_train, y_temp = train_test_split(
        x,
        y_encoded,
        test_size=0.30,
        random_state=random_state,
        stratify=y_encoded,
    )
    x_val, x_test, y_val, y_test = train_test_split(
        x_temp,
        y_temp,
        test_size=0.50,
        random_state=random_state,
        stratify=y_temp,
    )

    metric_key = METRIC_KEYS.get(primary_metric, primary_metric)
    comparison: Dict[str, Any] = {}
    best_name = None
    best_score = -1.0
    best_pipeline = None
    best_metrics: Dict[str, Any] = {}

    candidates = build_candidate_models(random_state=random_state)
    for name, estimator in candidates.items():
        logger.info("Training candidate: %s", name)
        preprocessor = build_preprocessor(feature_columns)
        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", estimator),
            ]
        )
        pipeline.fit(x_train, y_train)

        y_pred = pipeline.predict(x_val)
        if hasattr(pipeline, "predict_proba"):
            y_proba = pipeline.predict_proba(x_val)
        else:
            # Should not happen with calibrated SVM, but guard anyway
            classes = len(label_encoder.classes_)
            y_proba = np.zeros((len(y_pred), classes))
            y_proba[np.arange(len(y_pred)), y_pred] = 1.0

        metrics = evaluate_predictions(
            y_val,
            y_pred,
            y_proba,
            label_names=list(label_encoder.classes_),
        )
        comparison[name] = {
            "validation": {
                k: v
                for k, v in metrics.items()
                if k not in {"classification_report", "confusion_matrix"}
            }
        }
        score = float(metrics.get(metric_key, metrics["macro_f1"]))
        logger.info("%s validation %s=%.4f", name, metric_key, score)
        if score > best_score:
            best_score = score
            best_name = name
            best_pipeline = pipeline
            best_metrics = metrics

    assert best_pipeline is not None and best_name is not None

    # Refit best model on train+val, evaluate on held-out test
    x_trainval = np.concatenate([x_train.to_numpy(), x_val.to_numpy()], axis=0)
    y_trainval = np.concatenate([y_train, y_val], axis=0)
    # Keep DataFrame columns for ColumnTransformer
    import pandas as pd

    x_trainval_df = pd.DataFrame(x_trainval, columns=feature_columns)
    final_preprocessor = build_preprocessor(feature_columns)
    final_estimator = build_candidate_models(random_state=random_state)[best_name]
    final_pipeline = Pipeline(
        steps=[
            ("preprocessor", final_preprocessor),
            ("model", final_estimator),
        ]
    )
    final_pipeline.fit(x_trainval_df, y_trainval)

    y_test_pred = final_pipeline.predict(x_test)
    y_test_proba = final_pipeline.predict_proba(x_test)
    test_metrics = evaluate_predictions(
        y_test,
        y_test_pred,
        y_test_proba,
        label_names=list(label_encoder.classes_),
    )

    model_file = resolve_artifact_path(model_path)
    prep_file = resolve_artifact_path(preprocessor_path)
    meta_file = resolve_artifact_path(metadata_path)
    model_file.parent.mkdir(parents=True, exist_ok=True)
    prep_file.parent.mkdir(parents=True, exist_ok=True)
    meta_file.parent.mkdir(parents=True, exist_ok=True)

    # Persist full pipeline (includes preprocessor) as best_model
    joblib.dump(final_pipeline, model_file)
    # Also save preprocessor alone for inspection
    joblib.dump(final_pipeline.named_steps["preprocessor"], prep_file)
    joblib.dump(
        label_encoder,
        model_file.parent / "label_encoder.joblib",
    )

    metadata = {
        "model_name": best_name,
        "model_version": "1.0.0",
        "training_date": datetime.now(timezone.utc).isoformat(),
        "features": feature_columns,
        "classes": list(label_encoder.classes_),
        "primary_metric": metric_key,
        "primary_metric_validation_score": best_score,
        "metrics": {
            "validation_best": {
                k: v
                for k, v in best_metrics.items()
                if k not in {"classification_report", "confusion_matrix"}
            },
            "test": {
                k: v
                for k, v in test_metrics.items()
                if k not in {"classification_report", "confusion_matrix"}
            },
            "comparison": comparison,
        },
        "dataset": report.to_dict(),
        "artifact_paths": {
            "model": str(model_file),
            "preprocessor": str(prep_file),
            "label_encoder": str(model_file.parent / "label_encoder.joblib"),
        },
        "disclaimer": (
            "Educational model-based estimates only — not a medical diagnosis."
        ),
    }

    meta_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    # Save richer evaluation artifacts
    eval_dir = meta_file.parent / "evaluation_reports"
    eval_dir.mkdir(parents=True, exist_ok=True)
    (eval_dir / "classification_report_test.json").write_text(
        json.dumps(test_metrics["classification_report"], indent=2),
        encoding="utf-8",
    )
    (eval_dir / "confusion_matrix_test.json").write_text(
        json.dumps(
            {
                "labels": list(label_encoder.classes_),
                "matrix": test_metrics["confusion_matrix"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (eval_dir / "model_comparison.json").write_text(
        json.dumps(comparison, indent=2),
        encoding="utf-8",
    )

    print("=== Model Comparison (validation) ===")
    for name, payload in comparison.items():
        val = payload["validation"]
        print(
            f"{name:20s} accuracy={val['accuracy']:.4f} "
            f"macro_f1={val['macro_f1']:.4f} weighted_f1={val['weighted_f1']:.4f}"
        )
    print(f"\nSelected best model: {best_name} ({metric_key}={best_score:.4f})")
    print(
        f"Test macro_f1={test_metrics['macro_f1']:.4f} "
        f"accuracy={test_metrics['accuracy']:.4f}"
    )
    print(f"Saved model -> {model_file}")
    print(f"Saved metadata -> {meta_file}")

    return metadata
