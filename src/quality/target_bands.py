"""Target band definitions for clinker-quality and chemistry guardrails."""

from __future__ import annotations

from typing import Dict

TARGET_BANDS: Dict[str, Dict[str, float]] = {
    "Free CaO": {"ok_max": 1.5, "warning_max": 2.5},
    "C3S": {"ok_min": 55.0, "ok_max": 70.0, "warning_min": 50.0, "warning_max": 75.0},
    "C2S": {"ok_min": 10.0, "ok_max": 25.0, "warning_min": 5.0, "warning_max": 30.0},
    "C3A": {"ok_min": 4.0, "ok_max": 12.0, "warning_min": 2.0, "warning_max": 15.0},
    "C4AF": {"ok_min": 8.0, "ok_max": 18.0, "warning_min": 4.0, "warning_max": 24.0},
}


def get_target_band(target: str) -> Dict[str, float]:
    return TARGET_BANDS.get(target, {"ok_max": 100.0, "warning_max": 100.0})
