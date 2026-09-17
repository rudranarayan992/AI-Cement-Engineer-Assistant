"""Generate simple engineering recommendations based on physics validation.

Uses the existing physics validator to produce structured recommendations and
short action items.
"""
from __future__ import annotations

from typing import Dict, List

from src.validation.physics_constraints import validate_all


def generate_recommendations(chemistry: Dict[str, float], phases: Dict[str, float] | None = None) -> Dict[str, List[str]]:
    """Return short recommendations based on validation results.

    Args:
        chemistry: oxide composition + LSF/SM/AM keys
        phases: optional phase predictions

    Returns:
        dict with keys 'actions' and 'warnings'
    """
    result = validate_all(chemistry, phases or {})
    actions: List[str] = []
    warnings: List[str] = []

    if not result.get("valid", True):
        actions.append("Review raw material mix proportions and kiln firing profile.")
    for v in result.get("violations", []) or []:
        warnings.append(v)
    for w in result.get("warnings", []) or []:
        warnings.append(w)

    # Suggest typical engineering levers
    if chemistry.get("LSF", 0) < 0.95:
        actions.append("Increase limestone or high-Ca input to raise LSF toward target range.")
    if chemistry.get("LSF", 0) > 1.03:
        actions.append("Reduce calcareous feed or adjust kiln temperature to lower LSF.")

    return {"actions": actions, "warnings": warnings}
