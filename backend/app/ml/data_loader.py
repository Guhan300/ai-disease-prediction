"""Dataset loading and validation utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from app.core.logging import get_logger

logger = get_logger("ml.data_loader")


@dataclass
class DatasetReport:
    """Structured dataset inspection report."""

    path: str
    n_rows: int
    n_columns: int
    target_column: str
    feature_columns: List[str]
    missing_values: Dict[str, int]
    duplicate_rows: int
    constant_columns: List[str]
    class_counts: Dict[str, int]
    n_classes: int
    imbalance_ratio: float
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "n_rows": self.n_rows,
            "n_columns": self.n_columns,
            "target_column": self.target_column,
            "feature_columns": self.feature_columns,
            "missing_values": self.missing_values,
            "duplicate_rows": self.duplicate_rows,
            "constant_columns": self.constant_columns,
            "class_counts": self.class_counts,
            "n_classes": self.n_classes,
            "imbalance_ratio": self.imbalance_ratio,
            "notes": self.notes,
        }


def resolve_path(path: str | Path) -> Path:
    """Resolve dataset path relative to project root when needed."""
    p = Path(path)
    if p.is_file():
        return p
    # Try from project root (two parents above backend/app)
    project_root = Path(__file__).resolve().parents[3]
    candidate = project_root / path
    if candidate.is_file():
        return candidate
    raise FileNotFoundError(
        f"Dataset not found at '{path}'. Place a CSV at DATASET_PATH "
        "or run: python scripts/generate_dataset.py"
    )


def load_dataset(path: str | Path) -> pd.DataFrame:
    """Load a CSV disease/symptom dataset."""
    resolved = resolve_path(path)
    df = pd.read_csv(resolved)
    logger.info("Loaded dataset %s shape=%s", resolved, df.shape)
    return df


def validate_dataset(
    df: pd.DataFrame,
    target_column: str,
    *,
    drop_duplicates: bool = False,
) -> tuple[pd.DataFrame, DatasetReport]:
    """
    Inspect and lightly clean a dataset without silent destructive changes.

    Duplicates are only dropped when drop_duplicates=True (training opt-in).
    """
    notes: List[str] = []
    if target_column not in df.columns:
        raise ValueError(
            f"Target column '{target_column}' not found. "
            f"Available columns: {list(df.columns)}"
        )

    feature_columns = [c for c in df.columns if c != target_column]
    if not feature_columns:
        raise ValueError("No feature columns found besides the target.")

    missing = {c: int(df[c].isna().sum()) for c in df.columns if df[c].isna().any()}
    dup_count = int(df.duplicated().sum())
    constant_cols = [c for c in feature_columns if df[c].nunique(dropna=False) <= 1]

    class_counts = df[target_column].value_counts().to_dict()
    class_counts = {str(k): int(v) for k, v in class_counts.items()}
    counts = list(class_counts.values()) or [1]
    imbalance_ratio = float(max(counts) / max(min(counts), 1))

    if missing:
        notes.append(f"Missing values detected in {len(missing)} columns.")
    if dup_count:
        notes.append(f"{dup_count} duplicate rows detected.")
    if constant_cols:
        notes.append(f"Constant columns: {constant_cols}")
    if imbalance_ratio >= 3:
        notes.append(
            f"Class imbalance ratio={imbalance_ratio:.2f}. "
            "Prefer macro_f1 over accuracy for model selection."
        )

    working = df.copy()
    if drop_duplicates and dup_count:
        before = len(working)
        working = working.drop_duplicates().reset_index(drop=True)
        notes.append(f"Dropped {before - len(working)} duplicate rows for training.")

    # Fill numeric NaNs with 0 for binary symptom matrices (documented)
    numeric_cols = working[feature_columns].select_dtypes(include="number").columns
    if working[numeric_cols].isna().any().any():
        working[numeric_cols] = working[numeric_cols].fillna(0)
        notes.append("Filled numeric missing feature values with 0.")

    report = DatasetReport(
        path="",
        n_rows=int(working.shape[0]),
        n_columns=int(working.shape[1]),
        target_column=target_column,
        feature_columns=feature_columns,
        missing_values=missing,
        duplicate_rows=dup_count,
        constant_columns=constant_cols,
        class_counts=class_counts,
        n_classes=len(class_counts),
        imbalance_ratio=imbalance_ratio,
        notes=notes,
    )
    return working, report


def print_report(report: DatasetReport) -> None:
    """Print a human-readable training dataset report."""
    print("\n=== Dataset Report ===")
    print(f"Rows: {report.n_rows} | Columns: {report.n_columns}")
    print(f"Target: {report.target_column} | Classes: {report.n_classes}")
    print(f"Features ({len(report.feature_columns)}): {report.feature_columns}")
    print(f"Missing values: {report.missing_values or 'none'}")
    print(f"Duplicate rows: {report.duplicate_rows}")
    print(f"Constant columns: {report.constant_columns or 'none'}")
    print(f"Imbalance ratio (max/min): {report.imbalance_ratio:.2f}")
    print("Class distribution:")
    for label, count in sorted(report.class_counts.items(), key=lambda x: -x[1]):
        print(f"  - {label}: {count}")
    if report.notes:
        print("Notes:")
        for note in report.notes:
            print(f"  * {note}")
    print("======================\n")
