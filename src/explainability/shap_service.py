"""SHAP-style explanation service for the AI Cement Engineer architecture."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping


def get_top_drivers(features: Mapping[str, Any] | None, target: str) -> List[Dict[str, Any]]:
    if not features:
        return []

    items = []
    for key, value in features.items():
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            continue
        items.append({
            "feature": str(key),
            "value": numeric_value,
            "positive_contribution": abs(numeric_value) if numeric_value >= 0 else 0.0,
            "negative_contribution": abs(numeric_value) if numeric_value < 0 else 0.0,
            "magnitude": abs(numeric_value),
            "engineering_interpretation": f"Feature '{key}' contributes to the modeled association for {target} and should be checked against process and lab context.",
        })
    return sorted(items, key=lambda x: x["magnitude"], reverse=True)[:5]


def compute_shap_response(features: Mapping[str, Any] | None, target: str) -> Dict[str, Any]:
    drivers = get_top_drivers(features, target)
    if not drivers:
        return {
            "status": "RESEARCH DATA BLOCKED",
            "top_drivers": [],
            "message": "Qualified measured clinker labels with traceable sample/process/laboratory provenance are required for real clinker ML.",
        }

    return {
        "status": "AVAILABLE",
        "top_drivers": drivers,
        "model_association_note": "This is a model association view, not evidence of causal mechanism.",
        "causal_note": "Causal mechanism must be established with measured process, chemistry, and lab evidence before using SHAP outputs as causation claims.",
    }
