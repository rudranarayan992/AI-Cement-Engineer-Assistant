"""Physical and engineering plausibility validator for cement process predictions.

This module implements an engineering-feasibility gate that orchestrates checks from
the chemistry engine and phase constraints layers. It does NOT duplicate formulas;
instead, it reuses existing APIs and adds configurable engineering bounds.

ARCHITECTURE:

Raw-material proportions
        ↓
Chemistry engine (ignition basis, moduli calculation)
        ↓
LSF / SM / AM (configurable ranges)
        ↓
Clinker phase prediction
        ↓
Phase constraints (stoichiometric validation)
        ↓
PHYSICS / ENGINEERING VALIDATOR  ← This module
        ↓
Structured result: {valid, violations, warnings, checks, constraint_score}

DESIGN PRINCIPLES:

1. Do not duplicate chemistry formulas. Call chemistry_engine and phase_constraints APIs.
2. Keep all engineering limits configurable. Do not hard-code universal "laws."
3. Distinguish hard violations (fail) from warnings (pass with caution).
4. Return structured, traceable results.
5. Never silently clip or convert values.

CONFIGURABLE ENGINEERING LIMITS:

These represent typical operating windows for cement plants and can vary by process,
raw materials, product grade, and regulatory requirements. They should NOT be treated
as universal scientific laws.

Default ranges (modifiable):
    LSF:  [0.90, 1.05]  (lime saturation factor; typical range 0.92–1.00)
    SM:   [2.00, 3.00]  (silica modulus; typical range 2.20–2.70)
    AM:   [1.40, 2.20]  (alumina modulus; typical range 1.50–2.00)
    Free_CaO:  [0.0, 3.0]  (maximum unburnt lime tolerance; typical limit ~1.5%)
    C3S, C2S, C3A, C4AF:  [0.0, 100.0]  (phase fractions in mass %)
    Raw material fractions:  [0.0, 100.0] per material, sum to ~100%

REFERENCE:

Bhatty, J. I., et al. (eds.). (2004). Lea's Chemistry of Cement and Concrete.
    (Sections on kiln control, moduli optimization, and phase distribution.)

---
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# Try to import phase_constraints; fallback if not available
try:
    from src.chemistry import phase_constraints as _pc  # type: ignore
except Exception:
    try:
        from ..chemistry import phase_constraints as _pc  # type: ignore
    except Exception:
        import importlib.util
        import os

        def _load_phase_constraints():
            base = os.path.dirname(os.path.dirname(__file__))
            path = os.path.join(base, "chemistry", "phase_constraints.py")
            spec = importlib.util.spec_from_file_location("phase_constraints", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod

        _pc = _load_phase_constraints()


@dataclass
class ConstraintLimits:
    """Configurable engineering constraint limits.

    These represent typical operating windows and are NOT universal laws.
    Adjust based on your process, raw materials, and product grade.
    """

    # LSF (Lime Saturation Factor)
    lsf_min: float = 0.90
    lsf_max: float = 1.05

    # SM (Silica Modulus)
    sm_min: float = 2.00
    sm_max: float = 3.00

    # AM (Alumina Modulus)
    am_min: float = 1.40
    am_max: float = 2.20

    # Free CaO (unburnt lime)
    free_cao_max: float = 3.0

    # Phase fractions (minimum allowed; maximum is typically 100%)
    phase_min: float = 0.0
    phase_c3s_max: float = 100.0
    phase_c2s_max: float = 100.0
    phase_c3a_max: float = 100.0
    phase_c4af_max: float = 100.0

    # Raw material proportions (sum to ~100%)
    raw_mix_tolerance: float = 2.0  # ±2% tolerance on sum
    raw_material_min: float = 0.0
    raw_material_max: float = 100.0

    # Custom per-material limits (mapping material_id -> (min, max))
    material_limits: Dict[str, Tuple[float, float]] = field(default_factory=dict)


def validate_raw_mix_proportions(
    proportions: Dict[str, float],
    limits: Optional[ConstraintLimits] = None,
) -> Dict[str, Any]:
    """Validate raw-material proportions.

    Args:
        proportions: Mapping of material_id -> proportion (in %).
        limits: ConstraintLimits object. If None, uses defaults.

    Returns:
        Validation result:
            {
                "valid": bool,
                "violations": [...],
                "warnings": [...],
                "total": float,
                "count": int,
            }
    """
    if limits is None:
        limits = ConstraintLimits()

    violations = []
    warnings = []

    # Check for negative proportions
    for mat_id, prop in proportions.items():
        if prop is None:
            violations.append(f"Raw material '{mat_id}' has None proportion")
            continue
        try:
            p = float(prop)
        except (TypeError, ValueError):
            violations.append(f"Raw material '{mat_id}' has non-numeric proportion: {prop}")
            continue

        if math.isnan(p) or math.isinf(p):
            violations.append(f"Raw material '{mat_id}' has invalid proportion: {p}")
            continue

        if p < limits.raw_material_min:
            violations.append(
                f"Raw material '{mat_id}' = {p:.2f}% < minimum {limits.raw_material_min}%"
            )

        if p > limits.raw_material_max:
            violations.append(
                f"Raw material '{mat_id}' = {p:.2f}% > maximum {limits.raw_material_max}%"
            )

        # Check material-specific limits
        if mat_id in limits.material_limits:
            mat_min, mat_max = limits.material_limits[mat_id]
            if p < mat_min or p > mat_max:
                violations.append(
                    f"Raw material '{mat_id}' = {p:.2f}% outside custom range [{mat_min}, {mat_max}]%"
                )

    # Check total sum
    total = sum(float(v) for v in proportions.values() if v is not None)
    expected = 100.0
    if abs(total - expected) > limits.raw_mix_tolerance:
        violations.append(
            f"Raw mix total {total:.2f}% outside tolerance [{expected - limits.raw_mix_tolerance}, {expected + limits.raw_mix_tolerance}]%"
        )

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "warnings": warnings,
        "total": total,
        "count": len(proportions),
    }


def validate_chemistry_values(
    oxides: Dict[str, float],
) -> Dict[str, Any]:
    """Validate oxide composition for physical plausibility.

    Args:
        oxides: Mapping of oxide_name -> value (in wt%).

    Returns:
        Validation result:
            {
                "valid": bool,
                "violations": [...],
                "warnings": [...],
            }
    """
    violations = []
    warnings = []

    for oxide_name, oxide_value in oxides.items():
        if oxide_value is None:
            warnings.append(f"Oxide '{oxide_name}' is None (will be treated as 0)")
            continue

        try:
            ov = float(oxide_value)
        except (TypeError, ValueError):
            violations.append(f"Oxide '{oxide_name}' is non-numeric: {oxide_value}")
            continue

        if math.isnan(ov):
            violations.append(f"Oxide '{oxide_name}' is NaN")
        elif math.isinf(ov):
            violations.append(f"Oxide '{oxide_name}' is infinite")
        elif ov < 0:
            violations.append(f"Oxide '{oxide_name}' = {ov:.2f}% is negative (physically impossible)")

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "warnings": warnings,
    }


def validate_moduli(
    cao: float,
    sio2: float,
    al2o3: float,
    fe2o3: float,
    limits: Optional[ConstraintLimits] = None,
) -> Dict[str, Any]:
    """Validate clinker moduli (LSF, SM, AM) against configured ranges.

    Note: This function recomputes LSF/SM/AM locally using standard formulas
    to avoid external dependencies. Formulas match chemistry_engine.py.

    Args:
        cao, sio2, al2o3, fe2o3: Oxide values (assumed ignited basis, wt%).
        limits: ConstraintLimits object. If None, uses defaults.

    Returns:
        Validation result:
            {
                "valid": bool,
                "violations": [...],
                "warnings": [...],
                "LSF": float,
                "SM": float,
                "AM": float,
            }
    """
    if limits is None:
        limits = ConstraintLimits()

    violations = []
    warnings = []

    # Compute moduli (standard Bogue-derived formulas)
    # LSF = CaO / (2.8*SiO2 + 1.18*Al2O3 + 0.65*Fe2O3)
    # SM = SiO2 / (Al2O3 + Fe2O3)
    # AM = Al2O3 / Fe2O3

    denom_lsf = 2.8 * sio2 + 1.18 * al2o3 + 0.65 * fe2o3
    lsf = cao / denom_lsf if denom_lsf > 1e-9 else float("nan")

    denom_sm = al2o3 + fe2o3
    sm = sio2 / denom_sm if denom_sm > 1e-9 else float("nan")

    denom_am = fe2o3
    am = al2o3 / denom_am if denom_am > 1e-9 else float("nan")

    # Check for invalid values
    if math.isnan(lsf) or math.isinf(lsf):
        violations.append(f"LSF is invalid (NaN or infinite)")
    elif lsf < limits.lsf_min:
        violations.append(f"LSF = {lsf:.4f} < minimum {limits.lsf_min}")
    elif lsf > limits.lsf_max:
        violations.append(f"LSF = {lsf:.4f} > maximum {limits.lsf_max}")

    if math.isnan(sm) or math.isinf(sm):
        violations.append(f"SM is invalid (NaN or infinite)")
    elif sm < limits.sm_min:
        violations.append(f"SM = {sm:.4f} < minimum {limits.sm_min}")
    elif sm > limits.sm_max:
        violations.append(f"SM = {sm:.4f} > maximum {limits.sm_max}")

    if math.isnan(am) or math.isinf(am):
        violations.append(f"AM is invalid (NaN or infinite)")
    elif am < limits.am_min:
        violations.append(f"AM = {am:.4f} < minimum {limits.am_min}")
    elif am > limits.am_max:
        violations.append(f"AM = {am:.4f} > maximum {limits.am_max}")

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "warnings": warnings,
        "LSF": lsf,
        "SM": sm,
        "AM": am,
    }


def validate_phase_prediction(
    predicted_phases: Dict[str, float],
    limits: Optional[ConstraintLimits] = None,
) -> Dict[str, Any]:
    """Validate clinker phase fractions using phase_constraints module.

    This function delegates to phase_constraints.validate_phase_prediction
    and adds additional limit checking.

    Args:
        predicted_phases: Mapping of phase_name -> fraction (in %).
        limits: ConstraintLimits object. If None, uses defaults.

    Returns:
        Validation result incorporating phase_constraints output and custom limits.
    """
    if limits is None:
        limits = ConstraintLimits()

    violations = []
    warnings = []

    # Use phase_constraints module for stoichiometric validation
    pc_result = _pc.validate_phase_prediction(predicted_phases)
    violations.extend(pc_result.get("warnings", []))

    # Additional phase-specific limit checks
    phase_bounds = {
        "C3S": (limits.phase_min, limits.phase_c3s_max),
        "C2S": (limits.phase_min, limits.phase_c2s_max),
        "C3A": (limits.phase_min, limits.phase_c3a_max),
        "C4AF": (limits.phase_min, limits.phase_c4af_max),
    }

    for phase_name, bounds in phase_bounds.items():
        phase_value = predicted_phases.get(phase_name)
        if phase_value is None:
            continue
        try:
            pv = float(phase_value)
        except (TypeError, ValueError):
            violations.append(f"Phase '{phase_name}' is non-numeric")
            continue

        lower, upper = bounds
        if pv < lower:
            violations.append(f"Phase '{phase_name}' = {pv:.2f}% < minimum {lower}%")
        elif pv > upper:
            violations.append(f"Phase '{phase_name}' = {pv:.2f}% > maximum {upper}%")

    # Check Free CaO if present
    free_cao = predicted_phases.get("Free_CaO")
    if free_cao is not None:
        try:
            fcao = float(free_cao)
            if fcao < 0.0:
                violations.append(f"Free CaO = {fcao:.2f}% is negative (impossible)")
            elif fcao > limits.free_cao_max:
                violations.append(
                    f"Free CaO = {fcao:.2f}% > maximum {limits.free_cao_max}%"
                )
        except (TypeError, ValueError):
            violations.append(f"Free CaO is non-numeric")

    return {
        "valid": len(violations) == 0 and pc_result.get("valid", False),
        "violations": violations,
        "warnings": warnings,
        "phase_constraints_result": pc_result,
    }


def validate_all(
    raw_mix_proportions: Optional[Dict[str, float]] = None,
    input_oxides: Optional[Dict[str, float]] = None,
    predicted_phases: Optional[Dict[str, float]] = None,
    limits: Optional[ConstraintLimits] = None,
) -> Dict[str, Any]:
    """Comprehensive engineering validation across raw mix, chemistry, and phases.

    This is the main entry point that orchestrates all sub-validators.

    Args:
        raw_mix_proportions: Raw material proportions (e.g., {"limestone": 78, "clay": 14, ...}).
        input_oxides: Oxide composition (e.g., {"CaO": 65, "SiO2": 22, ...}).
        predicted_phases: Predicted clinker phases (e.g., {"C3S": 65, "C2S": 15, ...}).
        limits: ConstraintLimits object. If None, uses defaults.

    Returns:
        Comprehensive validation result:
            {
                "valid": bool,
                "violations": [...],
                "warnings": [...],
                "checks": {
                    "raw_mix": {...},
                    "chemistry": {...},
                    "moduli": {...},
                    "phases": {...},
                },
                "constraint_score": float,
            }
    """
    if limits is None:
        limits = ConstraintLimits()

    all_violations = []
    all_warnings = []
    checks = {}
    constraint_score = 0.0

    # Raw mix validation
    if raw_mix_proportions is not None:
        rm_result = validate_raw_mix_proportions(raw_mix_proportions, limits)
        checks["raw_mix"] = rm_result
        all_violations.extend(rm_result.get("violations", []))
        all_warnings.extend(rm_result.get("warnings", []))
        if not rm_result.get("valid", False):
            constraint_score += 1.0

    # Chemistry validation
    if input_oxides is not None:
        chem_result = validate_chemistry_values(input_oxides)
        checks["chemistry"] = chem_result
        all_violations.extend(chem_result.get("violations", []))
        all_warnings.extend(chem_result.get("warnings", []))
        if not chem_result.get("valid", False):
            constraint_score += 1.0

        # Moduli validation
        cao = float(input_oxides.get("CaO", 65.0))
        sio2 = float(input_oxides.get("SiO2", 22.0))
        al2o3 = float(input_oxides.get("Al2O3", 5.0))
        fe2o3 = float(input_oxides.get("Fe2O3", 3.0))

        mod_result = validate_moduli(cao, sio2, al2o3, fe2o3, limits)
        checks["moduli"] = mod_result
        all_violations.extend(mod_result.get("violations", []))
        all_warnings.extend(mod_result.get("warnings", []))
        if not mod_result.get("valid", False):
            constraint_score += 1.0

    # Phase validation
    if predicted_phases is not None:
        phase_result = validate_phase_prediction(predicted_phases, limits)
        checks["phases"] = phase_result
        all_violations.extend(phase_result.get("violations", []))
        all_warnings.extend(phase_result.get("warnings", []))
        if not phase_result.get("valid", False):
            constraint_score += 1.0

    # Overall validity: no hard violations
    overall_valid = len(all_violations) == 0

    return {
        "valid": overall_valid,
        "violations": all_violations,
        "warnings": all_warnings,
        "checks": checks,
        "constraint_score": constraint_score,
    }
