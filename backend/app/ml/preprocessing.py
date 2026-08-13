"""Preprocessing pipeline construction."""

from __future__ import annotations

from typing import List, Tuple

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler


def split_xy(
    df: pd.DataFrame,
    target_column: str,
) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    """Split features/target and return feature names."""
    feature_columns = [c for c in df.columns if c != target_column]
    x = df[feature_columns].copy()
    y = df[target_column].astype(str).copy()
    return x, y, feature_columns


def build_preprocessor(feature_columns: List[str]) -> ColumnTransformer:
    """
    Build a ColumnTransformer.

    Binary symptom datasets are scaled for linear/SVM models; trees tolerate this.
    """
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), feature_columns),
        ],
        remainder="drop",
    )


def build_label_encoder(y: pd.Series) -> LabelEncoder:
    """Fit a label encoder on target labels."""
    encoder = LabelEncoder()
    encoder.fit(y)
    return encoder
