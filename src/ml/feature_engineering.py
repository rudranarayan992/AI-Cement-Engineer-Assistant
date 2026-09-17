"""Feature engineering helpers for the AI Cement Engineer pipeline."""

from __future__ import annotations

from typing import Iterable, Sequence

import pandas as pd


def normalize_feature_names(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    normalized.columns = [str(col).strip() for col in normalized.columns]
    return normalized


def safe_numeric_conversion(frame: pd.DataFrame, columns: Sequence[str] | None = None) -> pd.DataFrame:
    cleaned = frame.copy()
    target_cols = list(columns) if columns is not None else list(cleaned.columns)
    for col in target_cols:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")
    return cleaned


def apply_missing_value_policy(frame: pd.DataFrame, *, fill_value: float | None = None) -> pd.DataFrame:
    cleaned = frame.copy()
    for col in cleaned.select_dtypes(include="number").columns:
        if fill_value is None:
            cleaned[col] = cleaned[col].fillna(cleaned[col].median())
        else:
            cleaned[col] = cleaned[col].fillna(fill_value)
    return cleaned


def build_ml_feature_matrix(
    frame: pd.DataFrame,
    *,
    target_column: str | None = None,
    exclude_columns: Iterable[str] | None = None,
) -> tuple[pd.DataFrame, pd.Series | None]:
    cleaned = normalize_feature_names(frame)
    cleaned = safe_numeric_conversion(cleaned)
    cleaned = apply_missing_value_policy(cleaned)

    excluded = set(exclude_columns or [])
    feature_columns = [col for col in cleaned.columns if col not in excluded and (target_column is None or col != target_column)]
    X = cleaned[feature_columns].copy()

    if target_column is None or target_column not in cleaned.columns:
        return X, None

    y = cleaned[target_column].copy()
    return X, y
