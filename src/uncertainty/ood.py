"""Out-of-distribution and uncertainty monitoring utilities.

This module intentionally stays separate from model training and validation.
It provides feature-space diagnostics that can later wrap both baseline ML
and PIML models without entangling the training pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Sequence

import numpy as np
import pandas as pd


@dataclass
class OODConfig:
    """Configuration for feature-space OOD checks.

    These thresholds are intentionally simple and configurable. For engineering
    decisions they should be calibrated on historical process data rather than
    treated as universal laws.
    """

    z_score_threshold: float = 3.0
    mahalanobis_threshold: float = 3.0
    min_confidence: float = 0.5
    epsilon: float = 1e-6


@dataclass
class FeatureReferenceStats:
    """Reference distribution summary for feature-space monitoring."""

    feature_names: List[str]
    mean: Dict[str, float]
    std: Dict[str, float]
    covariance: np.ndarray


class FeatureOODMonitor:
    """Compute OOD scores from a feature-reference distribution.

    The monitor stores a reference mean and covariance for a set of feature
    columns. New samples are measured against this reference using z-scores and
    a Mahalanobis distance.
    """

    def __init__(self, feature_names: Sequence[str] | None = None, config: OODConfig | None = None):
        self.config = config or OODConfig()
        self.feature_names = list(feature_names) if feature_names is not None else []
        self.reference: FeatureReferenceStats | None = None

    def fit(self, data: Mapping[str, Sequence[float]] | pd.DataFrame) -> FeatureReferenceStats:
        """Fit the reference statistics from training data."""
        df = self._to_dataframe(data)
        if df.empty:
            raise ValueError("Reference data cannot be empty.")

        feature_names = list(df.columns)
        if not feature_names:
            raise ValueError("Reference data has no feature columns.")

        self.feature_names = feature_names
        means = df.mean(axis=0).to_dict()
        std = df.std(axis=0, ddof=0)
        std = std.replace(0, 1.0)
        std_map = std.to_dict()

        covariance = df.cov(ddof=0).to_numpy(dtype=float)
        if covariance.size == 0:
            covariance = np.eye(len(feature_names), dtype=float)
        elif covariance.shape == (1, 1):
            covariance = np.asarray([[max(float(covariance[0, 0]), 1.0)]], dtype=float)

        # Stabilize near-singular covariance for numerical robustness.
        covariance = covariance + np.eye(covariance.shape[0], dtype=float) * self.config.epsilon

        self.reference = FeatureReferenceStats(
            feature_names=feature_names,
            mean=means,
            std=std_map,
            covariance=covariance,
        )
        return self.reference

    def evaluate(self, sample: Mapping[str, float] | pd.DataFrame | Sequence[float]) -> Dict[str, Any]:
        """Evaluate one sample against the fitted reference distribution."""
        if self.reference is None:
            raise ValueError("FeatureOODMonitor is not fitted. Call fit() before evaluate().")

        features = self._normalize_sample(sample)
        if len(features) != len(self.reference.feature_names):
            raise ValueError(
                f"Expected {len(self.reference.feature_names)} features, got {len(features)}. "
                f"Available keys: {self.reference.feature_names}"
            )

        mean_vector = np.asarray([self.reference.mean[name] for name in self.reference.feature_names], dtype=float)
        std_vector = np.asarray([self.reference.std[name] for name in self.reference.feature_names], dtype=float)
        centered = features - mean_vector

        z_scores = np.abs(centered / np.clip(std_vector, self.config.epsilon, None))
        max_abs_z = float(np.max(z_scores)) if z_scores.size else 0.0

        cov_inv = np.linalg.pinv(self.reference.covariance)
        mahal_distance = float(np.sqrt(max(0.0, centered.T @ cov_inv @ centered)))

        ood_flag = bool(max_abs_z > self.config.z_score_threshold or mahal_distance > self.config.mahalanobis_threshold)

        normalized_distance = min(1.0, max(0.0, mahal_distance / max(self.config.mahalanobis_threshold, 1.0)))
        confidence = max(
            0.0,
            1.0 - normalized_distance,
        )
        confidence = max(self.config.min_confidence, confidence) if not ood_flag else max(0.0, confidence)

        warnings: List[str] = []
        if ood_flag:
            warnings.append(
                "Feature-space out-of-distribution warning: sample exceeds reference z-score or Mahalanobis distance."
            )

        for idx, name in enumerate(self.reference.feature_names):
            if z_scores[idx] > self.config.z_score_threshold:
                warnings.append(
                    f"Feature '{name}' is {z_scores[idx]:.2f} standard deviations from the reference mean."
                )

        return {
            "ood_flag": ood_flag,
            "valid": not ood_flag,
            "max_abs_z_score": round(max_abs_z, 4),
            "mahalanobis_distance": round(mahal_distance, 4),
            "confidence": round(float(confidence), 4),
            "score": round(float(max(max_abs_z, mahal_distance)), 4),
            "warnings": warnings,
            "feature_names": list(self.reference.feature_names),
        }

    def _normalize_sample(self, sample: Mapping[str, float] | pd.DataFrame | Sequence[float]) -> np.ndarray:
        """Normalize a single sample into a feature vector aligned with the reference."""
        if isinstance(sample, pd.DataFrame):
            if sample.shape[0] != 1:
                raise ValueError("DataFrame sample must contain exactly one row for single-sample evaluation.")
            missing = [name for name in self.reference.feature_names if name not in sample.columns]
            if missing:
                raise ValueError(f"Missing required features for evaluation: {missing}")
            row = sample.iloc[0]
            values = [float(row[name]) for name in self.reference.feature_names]
            return np.asarray(values, dtype=float)

        if isinstance(sample, Mapping):
            missing = [name for name in self.reference.feature_names if name not in sample]
            if missing:
                raise ValueError(f"Missing required features for evaluation: {missing}")
            values = [float(sample[name]) for name in self.reference.feature_names]
            return np.asarray(values, dtype=float)

        if isinstance(sample, Sequence) and not isinstance(sample, (str, bytes)):
            if len(sample) != len(self.reference.feature_names):
                raise ValueError(
                    f"Sequence length mismatch: expected {len(self.reference.feature_names)}, got {len(sample)}."
                )
            return np.asarray([float(v) for v in sample], dtype=float)

        raise TypeError("Sample must be a mapping, pandas DataFrame, or sequence of numeric values.")

    def _to_dataframe(self, data: Mapping[str, Sequence[float]] | pd.DataFrame) -> pd.DataFrame:
        """Coerce supported data types into a pandas DataFrame."""
        if isinstance(data, pd.DataFrame):
            return data.copy()
        if isinstance(data, Mapping):
            return pd.DataFrame(data)
        raise TypeError("Reference data must be a mapping or pandas.DataFrame.")


class PredictionUncertaintyWrapper:
    """Generic adapter for exposing OOD and uncertainty around a prediction.

    This wrapper is intentionally model-agnostic. It is meant to wrap either a
    baseline ML predictor or a PIML predictor later, without mixing in training
    logic or engineering validation logic.
    """

    def __init__(self, monitor: FeatureOODMonitor, model_name: str = "model"):
        self.monitor = monitor
        self.model_name = model_name

    def assess(self, sample: Mapping[str, float] | pd.DataFrame | Sequence[float], prediction: float) -> Dict[str, Any]:
        """Return uncertainty metadata around a prediction and feature sample."""
        audit = self.monitor.evaluate(sample)
        risk = max(0.0, min(1.0, audit["score"] / max(1.0, self.monitor.config.mahalanobis_threshold + 1.0)))
        uncertainty = round(float(risk), 4)
        confidence = round(float(max(0.0, 1.0 - uncertainty)), 4)

        if audit["ood_flag"]:
            confidence = max(0.0, confidence - 0.2)

        return {
            "model": self.model_name,
            "prediction": float(prediction),
            "ood_flag": audit["ood_flag"],
            "valid": audit["valid"],
            "uncertainty": uncertainty,
            "confidence": confidence,
            "warnings": audit["warnings"],
            "details": {
                "max_abs_z_score": audit["max_abs_z_score"],
                "mahalanobis_distance": audit["mahalanobis_distance"],
            },
        }
