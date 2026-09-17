"""Reusable training entrypoints for benchmark and research targets.

This module intentionally preserves the repository's scientific gate: when a
qualified measured target does not exist, the target is skipped safely and the
status is recorded instead of fabricating a prediction model.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from src.ml.data_catalog import build_data_catalog
from src.ml.feature_engineering import build_ml_feature_matrix
from src.ml.target_registry import get_registered_targets, get_target_entry
from src.preprocessing.data_preprocessing import FEATURE_COLUMNS, TARGET_COLUMN, load_concrete_dataset, prepare_concrete_dataframe


MODEL_CANDIDATES = {
    "LinearRegression": LinearRegression(),
    "Ridge": Ridge(alpha=1.0),
    "RandomForest": RandomForestRegressor(random_state=42, n_estimators=200),
    "ExtraTrees": ExtraTreesRegressor(random_state=42, n_estimators=200),
    "GradientBoosting": GradientBoostingRegressor(random_state=42),
}


def _concrete_benchmark_result() -> Dict[str, Any]:
    df = prepare_concrete_dataframe(load_concrete_dataset())
    X, y = build_ml_feature_matrix(df, target_column=TARGET_COLUMN, exclude_columns=[])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = MODEL_CANDIDATES["RandomForest"]
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    metrics = {
        "R2": float(r2_score(y_test, preds)),
        "MAE": float(mean_absolute_error(y_test, preds)),
        "RMSE": float(np.sqrt(mean_squared_error(y_test, preds))),
        "samples": int(len(y_test)),
    }

    return {
        "target": "compressive_strength",
        "status": "AVAILABLE_BENCHMARK",
        "model": type(model).__name__,
        "metrics": metrics,
        "training_data_type": "CONCRETE BENCHMARK",
        "notes": "Concrete benchmark model is valid for benchmark use only and not for clinker-quality claims.",
    }


def train_all_eligible_targets(repo_root: str | Path | None = None) -> Dict[str, Any]:
    catalog = build_data_catalog(repo_root=repo_root)
    results: List[Dict[str, Any]] = []

    concrete = _concrete_benchmark_result()
    results.append(concrete)

    for target in get_registered_targets():
        if target == "compressive_strength":
            continue
        entry = get_target_entry(target)
        if entry["status"] == "BLOCKED":
            results.append({
                "target": target,
                "status": "BLOCKED",
                "reason": str(entry["notes"]),
                "training_data_type": "RESEARCH_DATA_BLOCKED",
            })

    return {
        "catalog": catalog,
        "results": results,
        "trained_targets": [result["target"] for result in results if result.get("status") in {"AVAILABLE_BENCHMARK"}],
        "blocked_targets": [result["target"] for result in results if result.get("status") == "BLOCKED"],
    }
