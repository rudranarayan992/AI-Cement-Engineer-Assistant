"""ML benchmarking framework for regression models.

This module provides utilities to:
- split datasets (random or chronological/group-aware)
- train a set of candidate regressors (Linear, Ridge, RandomForest, XGBoost, SVR, MLP)
- compute evaluation metrics (R², MAE, RMSE, MAPE)
- save trained models and a results summary CSV

Design principles:
- Do deterministic splits by seed unless chronological splitting is requested.
- Do not claim any target accuracy: report metrics transparently.
- Keep default settings conservative; allow parameter overrides.

Usage (python):
    from src.training.benchmark import benchmark_regressors
    results = benchmark_regressors(X, y, output_dir="models", random_state=42)

"""
from __future__ import annotations
import os
import json
from typing import Dict, Any, Sequence, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib

try:
    from xgboost import XGBRegressor
    _HAS_XGB = True
except Exception:
    XGBRegressor = None  # type: ignore
    _HAS_XGB = False


def _mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    # avoid division by zero; use stable definition
    denom = np.where(np.abs(y_true) < 1e-8, 1.0, np.abs(y_true))
    return float(np.mean(np.abs((y_true - y_pred) / denom)) * 100.0)


DEFAULT_REGRESSORS = {
    "Linear": LinearRegression,
    "Ridge": lambda: Ridge(alpha=1.0, random_state=0),
    "RandomForest": lambda: RandomForestRegressor(n_estimators=200, random_state=0, n_jobs=-1),
    "SVR": lambda: SVR(kernel="rbf", C=1.0),
    "MLP": lambda: MLPRegressor(hidden_layer_sizes=(100, ), random_state=0, max_iter=1000),
}

if _HAS_XGB:
    DEFAULT_REGRESSORS["XGBoost"] = lambda: XGBRegressor(n_estimators=200, random_state=0, verbosity=0)


def _evaluate(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    return {
        "R2": float(r2_score(y_true, y_pred)),
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "MAPE": float(_mape(y_true, y_pred)),
    }


def benchmark_regressors(
    X: pd.DataFrame,
    y: pd.Series,
    regressors: Optional[Dict[str, Any]] = None,
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_state: int = 42,
    chronological: bool = False,
    time_index: Optional[pd.Series] = None,
    output_dir: str = "models",
    target_name: str = "target",
) -> pd.DataFrame:
    """Benchmark multiple regressors on a single-target regression task.

    Parameters
    - X: feature matrix as DataFrame
    - y: target Series
    - regressors: mapping name->callable or estimator class. If None, use DEFAULT_REGRESSORS.
    - test_size, val_size: fractions of data for splits (train = 1 - test - val)
    - chronological: if True, perform chronological splits using `time_index`.
    - time_index: Series aligned with X to use for chronological splitting.
    - output_dir: directory where models and results will be saved.

    Returns a DataFrame summarizing metrics per model on train/val/test and file paths.
    """
    if regressors is None:
        regressors = DEFAULT_REGRESSORS

    os.makedirs(output_dir, exist_ok=True)

    # Basic split handling
    if chronological:
        if time_index is None:
            raise ValueError("chronological=True requires a time_index Series")
        # Sort by time_index
        order = np.argsort(time_index.values)
        Xs = X.iloc[order].reset_index(drop=True)
        ys = y.iloc[order].reset_index(drop=True)
        n = len(Xs)
        n_test = int(np.floor(test_size * n))
        n_val = int(np.floor(val_size * n))
        n_train = n - n_test - n_val
        if n_train <= 0:
            raise ValueError("Not enough samples for the requested splits")
        X_train = Xs.iloc[:n_train]
        y_train = ys.iloc[:n_train]
        X_val = Xs.iloc[n_train:n_train + n_val]
        y_val = ys.iloc[n_train:n_train + n_val]
        X_test = Xs.iloc[n_train + n_val:]
        y_test = ys.iloc[n_train + n_val:]
    else:
        # Randomized split
        X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
        # compute validation fraction relative to remaining
        val_rel = val_size / (1.0 - test_size) if (1.0 - test_size) > 0 else 0.0
        X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=val_rel, random_state=random_state)

    results = []

    for name, estimator_ctor in regressors.items():
        try:
            # instantiate estimator
            est = estimator_ctor() if callable(estimator_ctor) else estimator_ctor
        except Exception:
            # if a class was passed
            try:
                est = estimator_ctor
            except Exception as e:
                raise

        # Fit model
        est.fit(X_train, y_train)

        # Predictions
        y_train_pred = est.predict(X_train)
        y_val_pred = est.predict(X_val)
        y_test_pred = est.predict(X_test)

        # Metrics
        metrics_train = _evaluate(y_train.to_numpy(), np.asarray(y_train_pred))
        metrics_val = _evaluate(y_val.to_numpy(), np.asarray(y_val_pred))
        metrics_test = _evaluate(y_test.to_numpy(), np.asarray(y_test_pred))

        model_path = os.path.join(output_dir, f"{target_name}__{name}.joblib")
        joblib.dump(est, model_path)

        row = {
            "model": name,
            "model_path": model_path,
            "train_R2": metrics_train["R2"],
            "train_MAE": metrics_train["MAE"],
            "train_RMSE": metrics_train["RMSE"],
            "train_MAPE": metrics_train["MAPE"],
            "val_R2": metrics_val["R2"],
            "val_MAE": metrics_val["MAE"],
            "val_RMSE": metrics_val["RMSE"],
            "val_MAPE": metrics_val["MAPE"],
            "test_R2": metrics_test["R2"],
            "test_MAE": metrics_test["MAE"],
            "test_RMSE": metrics_test["RMSE"],
            "test_MAPE": metrics_test["MAPE"],
        }
        results.append(row)

    results_df = pd.DataFrame(results)
    csv_path = os.path.join(output_dir, f"{target_name}__benchmark_results.csv")
    results_df.to_csv(csv_path, index=False)

    # Save metadata about the run
    meta = {
        "n_samples": int(len(X)),
        "test_size": float(test_size),
        "val_size": float(val_size),
        "random_state": int(random_state),
        "chronological": bool(chronological),
        "has_xgboost": bool(_HAS_XGB),
    }
    with open(os.path.join(output_dir, f"{target_name}__benchmark_meta.json"), "w", encoding="utf8") as fh:
        json.dump(meta, fh, indent=2)

    return results_df


if __name__ == "__main__":
    print("This module provides `benchmark_regressors()` for programmatic use.")
