"""Constraint and validation rules for raw-mix screening."""

from __future__ import annotations

from typing import Dict, List


def validate_raw_mix(raw_mix: Dict[str, float]) -> Dict[str, object]:
    """Check whether chemistry and process values stay within expected ranges."""
    warnings: List[str] = []

    lsf = float(raw_mix.get("LSF", 0.0))
    sm = float(raw_mix.get("SM", 0.0))
    am = float(raw_mix.get("AM", 0.0))
    kiln_temp = float(raw_mix.get("kiln_temperature_c", 0.0))

    if lsf < 0.9 or lsf > 1.1:
        warnings.append("LSF is outside the typical operating window.")
    if sm < 1.8 or sm > 3.0:
        warnings.append("SM is outside the expected range for clinker production.")
    if am < 1.0 or am > 3.0:
        warnings.append("AM is outside the expected range for clinker formation.")
    if kiln_temp < 1200 or kiln_temp > 1500:
        warnings.append("Kiln temperature is outside the usual range for stable operation.")

    return {
        "is_valid": len(warnings) == 0,
        "warnings": warnings,
    }


def engineering_warning_summary(raw_mix: Dict[str, float]) -> str:
    """Convert validation results into a concise engineering note."""
    check = validate_raw_mix(raw_mix)
    if check["is_valid"]:
        return "No rule-based warnings triggered. The formulation remains in the expected operating range."
    return "Warning: Low-confidence prediction. The chemistry or process values may be outside the training range. " + " ".join(check["warnings"])
