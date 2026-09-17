"""Small utilities to compute simple prediction intervals and integrate OOD checks.

This module provides conservative prediction-interval estimates (using residual std)
and exposes a helper to format uncertainty metadata for predictions.
"""
from __future__ import annotations

import math
from typing import Dict, Optional

import numpy as np
from sklearn.utils import resample


def prediction_interval_from_residuals(prediction: float, residuals: list[float], coverage: float = 0.9) -> Dict[str, float]:
    """Compute a simple two-sided prediction interval using empirical residuals.

    Args:
        prediction: point estimate
        residuals: list of historical residuals (prediction - actual)
        coverage: desired coverage probability (0-1)

    Returns:
        dict with keys 'lower', 'upper', 'std'
    """
    if not residuals:
        return {"lower": prediction - 2.0, "upper": prediction + 2.0, "std": 2.0}

    arr = np.array(residuals)
    # Use empirical quantiles
    alpha = (1.0 - coverage) / 2.0
    lower_q = np.quantile(arr, alpha)
    upper_q = np.quantile(arr, 1 - alpha)

    lower = float(prediction + lower_q)
    upper = float(prediction + upper_q)
    std = float(np.std(arr))
    return {"lower": lower, "upper": upper, "std": std}


def as_uncertainty_schema(pi: Dict[str, float]) -> Dict[str, float]:
    return {"prediction_lower": pi["lower"], "prediction_upper": pi["upper"], "residual_std": pi["std"]}
