"""Model-evaluation helpers for regression-style cement and concrete targets."""

from __future__ import annotations

from typing import Any, Dict, Iterable

import numpy as np


def compute_regression_metrics(y_true: Iterable[float], y_pred: Iterable[float]) -> Dict[str, float]:
    y_true_array = np.asarray(list(y_true), dtype=float)
    y_pred_array = np.asarray(list(y_pred), dtype=float)

    residual = y_true_array - y_pred_array
    abs_error = np.abs(residual)
    percent_error = np.divide(
        abs_error,
        np.clip(np.abs(y_true_array), 1e-8, None),
        out=np.zeros_like(abs_error, dtype=float),
        where=np.abs(y_true_array) > 1e-8,
    )

    ss_res = float(np.sum(residual**2))
    ss_tot = float(np.sum((y_true_array - np.mean(y_true_array)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0

    mae = float(np.mean(abs_error))
    rmse = float(np.sqrt(np.mean(residual**2)))
    mape = float(np.mean(percent_error) * 100.0)
    bias = float(np.mean(residual))

    return {
        "R2": float(r2),
        "MAE": mae,
        "RMSE": rmse,
        "MAPE": mape,
        "Bias": bias,
        "Mean_Absolute_Percentage_Error": mape,
    }


def summarize_predictions(actual: Iterable[float], predicted: Iterable[float]) -> Dict[str, Any]:
    metrics = compute_regression_metrics(actual, predicted)
    return {
        "n_samples": int(len(list(actual))),
        "metrics": metrics,
    }
