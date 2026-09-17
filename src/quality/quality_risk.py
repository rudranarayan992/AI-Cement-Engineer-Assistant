"""Quality risk engine for clinker and chemistry predictions."""

from __future__ import annotations

from typing import Any, Dict, Mapping

from src.quality.target_bands import get_target_band


def assess_quality_risk(prediction: Mapping[str, Any]) -> Dict[str, Any]:
    target = str(prediction.get("target", "Unknown"))
    status = str(prediction.get("status", "RESEARCH_DATA_BLOCKED")).upper()
    if status in {"RESEARCH DATA BLOCKED", "SYNTHETIC DEMO", "BLOCKED"}:
        return {
            "target": target,
            "status": "DATA BLOCKED",
            "reason": "No qualified measured clinker dataset is available for a real clinker model.",
            "confidence": float(prediction.get("confidence", 0.0)),
            "uncertainty": float(prediction.get("uncertainty", 1.0)),
        }

    physics_status = str(prediction.get("physics_status", "UNKNOWN")).upper()
    ood_status = str(prediction.get("ood_status", "UNKNOWN")).upper()
    uncertainty = float(prediction.get("uncertainty", 0.0))
    confidence = float(prediction.get("confidence", 0.0))

    if physics_status not in {"OK", "PASS"}:
        level = "HIGH RISK"
    elif ood_status in {"OUT-OF-DISTRIBUTION", "OOD"}:
        level = "WARNING"
    elif uncertainty > 0.35 or confidence < 0.65:
        level = "WARNING"
    else:
        level = "OK"

    band = get_target_band(target)
    value = float(prediction.get("prediction", 0.0))
    if target == "Free CaO":
        if value > band.get("warning_max", 2.5):
            level = "HIGH RISK"
    elif target in {"C3S", "C2S", "C3A", "C4AF"}:
        low = band.get("warning_min")
        high = band.get("warning_max")
        if low is not None and value < low:
            level = "WARNING"
        if high is not None and value > high:
            level = "WARNING"

    return {
        "target": target,
        "status": level,
        "reason": "Quality risk assigned using prediction uncertainty, OOD state, and physics validation status.",
        "confidence": confidence,
        "uncertainty": uncertainty,
    }
