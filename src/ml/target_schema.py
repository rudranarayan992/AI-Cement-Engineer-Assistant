"""Define the standardized schema for clinker-quality prediction outputs."""

from __future__ import annotations

from typing import Any, Dict, Mapping


REQUIRED_TARGETS = {
    "Free CaO": {"unit": "%", "family": "clinker_quality"},
    "C3S": {"unit": "%", "family": "clinker_phase"},
    "C2S": {"unit": "%", "family": "clinker_phase"},
    "C3A": {"unit": "%", "family": "clinker_phase"},
    "C4AF": {"unit": "%", "family": "clinker_phase"},
}


def normalize_target_name(target: str) -> str:
    key = (target or "").strip()
    aliases = {
        "free_cao": "Free CaO",
        "free cao": "Free CaO",
        "c3s": "C3S",
        "c2s": "C2S",
        "c3a": "C3A",
        "c4af": "C4AF",
    }
    return aliases.get(key.lower(), key)


def build_prediction_schema(
    *,
    prediction: Any,
    target: str,
    unit: str,
    model_version: str,
    confidence: float,
    uncertainty: float,
    ood_status: str,
    physics_status: str,
    warnings: list[str] | None = None,
    provenance: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    schema = {
        "prediction": prediction,
        "target": normalize_target_name(target),
        "unit": unit,
        "model_version": model_version,
        "confidence": float(confidence),
        "uncertainty": float(uncertainty),
        "ood_status": str(ood_status).upper(),
        "physics_status": str(physics_status).upper(),
        "warnings": list(warnings or []),
        "provenance": dict(provenance or {}),
    }
    return schema
