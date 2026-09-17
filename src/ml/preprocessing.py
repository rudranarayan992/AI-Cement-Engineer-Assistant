"""Preprocessing helpers for the AI Cement Engineer prediction service."""

from __future__ import annotations

from typing import Any, Dict, Mapping


def coerce_feature_dict(raw_features: Mapping[str, Any] | None) -> Dict[str, float]:
    if not raw_features:
        raise ValueError("Feature set cannot be empty.")

    cleaned: Dict[str, float] = {}
    for key, value in raw_features.items():
        cleaned[str(key)] = float(value)
    return cleaned


def prepare_feature_vector(raw_features: Mapping[str, Any] | None) -> Dict[str, float]:
    return coerce_feature_dict(raw_features)
