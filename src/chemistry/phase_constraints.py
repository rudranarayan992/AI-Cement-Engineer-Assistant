"""Chemistry-informed validation layer for clinker phase predictions.

This module implements stoichiometric consistency checks, phase-reconstruction
residuals, and physical plausibility validation for predicted clinker mineralogy.

SCIENTIFIC CONTEXT:

This is NOT a clinker phase predictor. Instead, it is a validation and constraint
module that:

1. Takes predicted phase fractions (C3S, C2S, C3A, C4AF, optionally Free_CaO)
2. Reconstructs the oxide composition that would result if those phases were
   exactly formed (idealized stoichiometry)
3. Compares the reconstructed oxides against measured/input oxide composition
4. Detects physical implausibilities (negative phases, NaN, sums > 100%, etc.)
5. Returns structured validation results

IMPORTANT CAVEATS:

- Bogue calculations are empirical phase estimates; they do NOT represent exact
  measured mineralogy. Real clinker contains impurities, solid solutions, and
  non-idealized phases.
- XRD and laboratory measurements are the actual ground truth when available.
- Idealized stoichiometric formulas (e.g., C3S = 3CaO·SiO2) assume pure end-member
  phases, which is rarely true in practice.
- This module is a chemistry-informed plausibility check, not a physics law.

TERMINOLOGY:

- Predicted phases: output from an ML model or Bogue calculation (units: mass %)
- Input oxides: measured or calculated raw-meal/clinker oxide composition (units: wt%)
- Reconstructed oxides: oxide composition implied by the predicted phases via
  stoichiometric conversion
- Residuals: difference between reconstructed and input oxides
- Constraint scores: scalar metrics indicating plausibility

RESEARCH PURPOSE:

This module enables comparison of:

A. Unconstrained ML (baseline)
B. ML with chemistry-derived features (baseline + domain knowledge)
C. ML with physics/chemistry constraints (PIML)

The research question: "Do chemistry-informed constraints improve physical
plausibility and generalization?"

---

STOICHIOMETRIC REFERENCE (idealized phases, mass basis):

For reference, approximate molecular weights (g/mol):
    CaO  = 56.08
    SiO2 = 60.09
    Al2O3 = 101.96
    Fe2O3 = 159.69

Idealized end-member phases:
    C3S (3CaO·SiO2)  = 3*56.08 + 60.09 = 228.33 g/mol
    C2S (2CaO·SiO2)  = 2*56.08 + 60.09 = 172.25 g/mol
    C3A (3CaO·Al2O3) = 3*56.08 + 101.96 = 269.20 g/mol
    C4AF (4CaO·Al2O3·Fe2O3) = 4*56.08 + 101.96 + 159.69 = 485.61 g/mol

Oxide composition (wt%):
    C3S:  CaO=73.6%, SiO2=26.4%
    C2S:  CaO=65.2%, SiO2=34.8%
    C3A:  CaO=62.4%, Al2O3=37.6%
    C4AF: CaO=46.2%, Al2O3=21.0%, Fe2O3=32.8%
    Free CaO: 100% CaO

Sources: standard cement chemistry references (e.g., Lea's Chemistry of Cement and Concrete)

---
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

# Stoichiometric coefficients (oxide wt% per 100 g of phase)
# These are idealized; real clinker deviates.
PHASE_STOICHIOMETRY = {
    "C3S": {"CaO": 73.6, "SiO2": 26.4, "Al2O3": 0.0, "Fe2O3": 0.0},
    "C2S": {"CaO": 65.2, "SiO2": 34.8, "Al2O3": 0.0, "Fe2O3": 0.0},
    "C3A": {"CaO": 62.4, "Al2O3": 37.6, "SiO2": 0.0, "Fe2O3": 0.0},
    "C4AF": {"CaO": 46.2, "Al2O3": 21.0, "Fe2O3": 32.8, "SiO2": 0.0},
    "Free_CaO": {"CaO": 100.0, "SiO2": 0.0, "Al2O3": 0.0, "Fe2O3": 0.0},
}

MAJOR_OXIDES = ["CaO", "SiO2", "Al2O3", "Fe2O3"]
SUPPORTED_PHASES = sorted(PHASE_STOICHIOMETRY.keys())


def phase_to_oxide_reconstruction(
    predicted_phases: Dict[str, float],
    phase_basis: str = "mass_percent",
) -> Dict[str, float]:
    """Reconstruct oxide composition from predicted clinker phases.

    This function applies idealized stoichiometric coefficients to convert
    predicted phase fractions into an oxide composition.

    Args:
        predicted_phases: Mapping of phase name -> value (e.g., {"C3S": 65.0, "C2S": 15.0, ...})
        phase_basis: One of "mass_percent" (input sums to ~100) or "fraction" (sums to ~1.0).
                    Used only for validation messaging; calculation is basis-agnostic.

    Returns:
        Dictionary of oxide name -> reconstructed value (same units as input phases).

    Raises:
        ValueError: If invalid phase names or basis.

    Notes:
        - The reconstruction is linear: sum over phases of (phase_fraction * oxide_wt% per phase).
        - Missing phases are assumed to be 0.
        - Reconstructed oxides may not sum to 100% if predicted phases don't sum to 100%.
    """
    if phase_basis not in ("mass_percent", "fraction"):
        raise ValueError(f"Unsupported phase_basis '{phase_basis}'")

    # Validate phase names
    for name in predicted_phases.keys():
        if name not in SUPPORTED_PHASES:
            raise ValueError(f"Unknown phase '{name}'. Supported: {sorted(SUPPORTED_PHASES)}")

    # Initialize reconstructed oxides
    reconstructed = {oxide: 0.0 for oxide in MAJOR_OXIDES}

    # Linear superposition of phase contributions
    for phase_name, phase_value in predicted_phases.items():
        try:
            phase_val = float(phase_value)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid phase value for '{phase_name}': {phase_value}")

        if math.isnan(phase_val) or math.isinf(phase_val):
            raise ValueError(f"Phase '{phase_name}' has invalid value: {phase_val}")

        stoich = PHASE_STOICHIOMETRY[phase_name]
        for oxide, wt_pct in stoich.items():
            reconstructed[oxide] += phase_val * (wt_pct / 100.0)

    return reconstructed


def calculate_stoichiometric_residual(
    input_oxides: Dict[str, float],
    predicted_phases: Dict[str, float],
    normalize_by: str = "input",
) -> Dict[str, Any]:
    """Calculate residuals between input oxides and reconstructed oxides from phases.

    This function computes the difference between the measured/calculated oxide
    composition and the oxide composition implied by predicted clinker phases.

    A small residual suggests chemical consistency between oxides and phases.
    A large residual suggests physical implausibility or missing/incorrect phases.

    Args:
        input_oxides: Mapping of oxide name -> value (e.g., {"CaO": 65.0, ...}) in wt%.
        predicted_phases: Mapping of phase name -> value.
        normalize_by: One of "input", "reconstructed", or "none".
                     Affects how residuals are normalized (if at all).

    Returns:
        Dictionary containing:
            - "residuals": {oxide_name -> residual_value}
            - "residuals_normalized": {oxide_name -> normalized_residual} (if normalize_by != "none")
            - "total_residual": sum of absolute residuals
            - "root_mean_square_residual": RMS of residuals

    Notes:
        - Residuals are (input - reconstructed).
        - Normalization by input: residual / input (percent error if input != 0).
        - Normalization by reconstructed: residual / reconstructed (percent error if reconstructed != 0).
        - Missing oxide values in input are treated as 0.
    """
    if normalize_by not in ("input", "reconstructed", "none"):
        raise ValueError(f"Unsupported normalize_by: {normalize_by}")

    # Reconstruct oxides from phases
    reconstructed = phase_to_oxide_reconstruction(predicted_phases)

    # Compute raw residuals
    residuals = {}
    for oxide in MAJOR_OXIDES:
        input_val = float(input_oxides.get(oxide, 0.0)) if input_oxides.get(oxide) is not None else 0.0
        recon_val = reconstructed.get(oxide, 0.0)
        residuals[oxide] = input_val - recon_val

    # Compute normalized residuals
    residuals_normalized = {}
    if normalize_by == "input":
        for oxide, res in residuals.items():
            input_val = float(input_oxides.get(oxide, 1.0)) if input_oxides.get(oxide) is not None else 1.0
            if abs(input_val) < 1e-9:
                residuals_normalized[oxide] = float("nan")
            else:
                residuals_normalized[oxide] = res / input_val
    elif normalize_by == "reconstructed":
        for oxide, res in residuals.items():
            recon_val = reconstructed.get(oxide, 1.0)
            if abs(recon_val) < 1e-9:
                residuals_normalized[oxide] = float("nan")
            else:
                residuals_normalized[oxide] = res / recon_val

    # Compute aggregate metrics
    abs_residuals = [abs(r) for r in residuals.values() if not (isinstance(r, float) and math.isnan(r))]
    total_residual = sum(abs_residuals)
    rms_residual = math.sqrt(sum(r**2 for r in abs_residuals) / len(abs_residuals)) if abs_residuals else 0.0

    result = {
        "residuals": residuals,
        "total_residual": total_residual,
        "root_mean_square_residual": rms_residual,
        "reconstructed_oxides": reconstructed,
    }

    if normalize_by != "none":
        result["residuals_normalized"] = residuals_normalized

    return result


def calculate_phase_sum_residual(predicted_phases: Dict[str, float]) -> Dict[str, Any]:
    """Check whether predicted phase fractions sum to a plausible value.

    In idealized stoichiometry, phase fractions should sum to approximately 100%
    (if on a mass percent basis) or 1.0 (if on a fraction basis).

    However, real clinker contains minor phases, amorphous material, and free CaO
    not captured in the Bogue model. This function detects whether the sum is
    implausible.

    Args:
        predicted_phases: Mapping of phase name -> value.

    Returns:
        Dictionary containing:
            - "phase_sum": sum of predicted phase values
            - "sum_basis": "mass_percent" (if sum ~100) or "fraction" (if sum ~1) or "unknown"
            - "valid": True if sum is plausible
            - "warnings": List of warning strings
    """
    phase_sum = sum(float(v) for v in predicted_phases.values() if v is not None and not (isinstance(v, float) and math.isnan(v)))

    warnings = []
    valid = True
    sum_basis = "unknown"

    # Heuristic detection of basis
    if 99.0 <= phase_sum <= 101.0:
        sum_basis = "mass_percent"
    elif 0.99 <= phase_sum <= 1.01:
        sum_basis = "fraction"
    elif phase_sum < 50.0:
        # Likely fraction basis but incomplete
        sum_basis = "fraction"
        valid = False
        warnings.append(f"Phase sum {phase_sum:.3f} is implausibly low (incomplete phases)")
    else:
        sum_basis = "mass_percent"
        if phase_sum < 80.0 or phase_sum > 110.0:
            valid = False
            warnings.append(f"Phase sum {phase_sum:.3f} is outside typical range (80-110%)")

    return {
        "phase_sum": phase_sum,
        "sum_basis": sum_basis,
        "valid": valid,
        "warnings": warnings,
    }


def calculate_physical_bound_penalty(
    predicted_phases: Dict[str, float],
    phase_bounds: Optional[Dict[str, Tuple[float, float]]] = None,
) -> Dict[str, Any]:
    """Check predicted phase fractions against physical/chemical bounds.

    This function detects violations such as:
    - Negative phase fractions (physically impossible)
    - NaN or infinite predictions
    - Phase fractions exceeding reasonable upper bounds

    Args:
        predicted_phases: Mapping of phase name -> value.
        phase_bounds: Optional mapping of phase name -> (lower, upper) bounds.
                     If not provided, uses defaults:
                     All phases: [0.0, 100.0] for percent or [0.0, 1.0] for fraction.

    Returns:
        Dictionary containing:
            - "valid": True if all predictions satisfy bounds
            - "violations": List of violation messages
            - "penalty": scalar penalty score (0 if valid, > 0 otherwise)
            - "bound_status": {phase_name -> {"value": ..., "lower": ..., "upper": ..., "ok": ...}}
    """
    if phase_bounds is None:
        # Default bounds: assume phases are mass percents
        phase_bounds = {phase: (0.0, 100.0) for phase in SUPPORTED_PHASES}

    violations = []
    penalty = 0.0
    bound_status = {}

    for phase_name, phase_value in predicted_phases.items():
        if phase_name not in SUPPORTED_PHASES:
            continue

        bounds = phase_bounds.get(phase_name, (0.0, 100.0))
        lower, upper = float(bounds[0]), float(bounds[1])

        # Check for invalid values
        if phase_value is None or (isinstance(phase_value, float) and math.isnan(phase_value)):
            violations.append(f"Phase '{phase_name}' is NaN or missing")
            penalty += 10.0
            bound_status[phase_name] = {"value": phase_value, "lower": lower, "upper": upper, "ok": False}
            continue

        if isinstance(phase_value, float) and math.isinf(phase_value):
            violations.append(f"Phase '{phase_name}' is infinite")
            penalty += 10.0
            bound_status[phase_name] = {"value": phase_value, "lower": lower, "upper": upper, "ok": False}
            continue

        try:
            pv = float(phase_value)
        except (TypeError, ValueError):
            violations.append(f"Phase '{phase_name}' has non-numeric value: {phase_value}")
            penalty += 10.0
            bound_status[phase_name] = {"value": phase_value, "lower": lower, "upper": upper, "ok": False}
            continue

        # Check bounds
        ok = lower <= pv <= upper
        bound_status[phase_name] = {"value": pv, "lower": lower, "upper": upper, "ok": ok}

        if pv < lower:
            violations.append(f"Phase '{phase_name}' = {pv:.3f} < lower bound {lower}")
            penalty += abs(lower - pv)
        elif pv > upper:
            violations.append(f"Phase '{phase_name}' = {pv:.3f} > upper bound {upper}")
            penalty += abs(pv - upper)

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "penalty": penalty,
        "bound_status": bound_status,
    }


def validate_phase_prediction(
    predicted_phases: Dict[str, float],
    input_oxides: Optional[Dict[str, float]] = None,
    phase_bounds: Optional[Dict[str, Tuple[float, float]]] = None,
    max_residual_tolerance: float = 5.0,
) -> Dict[str, Any]:
    """Comprehensive validation of a predicted clinker phase composition.

    This is the main validation function that runs all checks and returns
    a structured result indicating physical plausibility.

    Args:
        predicted_phases: Predicted phase fractions (e.g., {"C3S": 65.0, "C2S": 15.0, ...})
        input_oxides: Measured or calculated oxide composition. If provided, stoichiometric
                     residuals are computed.
        phase_bounds: Custom bounds for phase fractions. If None, defaults to [0, 100].
        max_residual_tolerance: Maximum acceptable RMS residual (wt%) for phases to be
                               considered plausible. Default 5.0%.

    Returns:
        Comprehensive validation dictionary:
            {
                "valid": bool,
                "predicted_phases": {...},
                "input_oxides": {...},
                "reconstructed_oxides": {...} (if input_oxides provided),
                "phase_sum_check": {...},
                "bound_check": {...},
                "residual_check": {...} (if input_oxides provided),
                "warnings": [...],
                "constraint_score": float,
            }

    Notes:
        - valid=True only if no violations detected.
        - constraint_score ranges from 0 (perfect plausibility) to higher values (problems).
        - warnings are never suppressed; always review them.
    """
    warnings: List[str] = []
    constraint_score = 0.0

    # Phase sum validation
    phase_sum_result = calculate_phase_sum_residual(predicted_phases)
    if not phase_sum_result["valid"]:
        warnings.extend(phase_sum_result["warnings"])
        constraint_score += 1.0

    # Physical bound validation
    bound_result = calculate_physical_bound_penalty(predicted_phases, phase_bounds)
    if not bound_result["valid"]:
        warnings.extend(bound_result["violations"])
        constraint_score += bound_result["penalty"]

    # Stoichiometric residual validation
    residual_result = None
    if input_oxides is not None:
        residual_result = calculate_stoichiometric_residual(
            input_oxides, predicted_phases, normalize_by="input"
        )
        rms_res = residual_result.get("root_mean_square_residual", 0.0)
        if rms_res > max_residual_tolerance:
            warnings.append(
                f"Stoichiometric RMS residual {rms_res:.2f}% exceeds tolerance {max_residual_tolerance}%"
            )
            constraint_score += rms_res / max_residual_tolerance

    # Determine overall validity
    overall_valid = len(bound_result["violations"]) == 0 and phase_sum_result["valid"]

    result = {
        "valid": overall_valid,
        "predicted_phases": dict(predicted_phases),
        "phase_sum_check": phase_sum_result,
        "bound_check": bound_result,
        "warnings": warnings,
        "constraint_score": constraint_score,
    }

    if input_oxides is not None:
        result["input_oxides"] = dict(input_oxides)
        result["residual_check"] = residual_result

    return result


def constraint_loss_components(
    predicted_phases: Dict[str, float],
    input_oxides: Optional[Dict[str, float]] = None,
    phase_bounds: Optional[Dict[str, Tuple[float, float]]] = None,
) -> Dict[str, float]:
    """Compute individual loss components for PIML training.

    This function breaks down constraint violations into separate loss terms
    that can be combined in a PIML loss function.

    Returns a dictionary with loss components:
        {
            "L_stoich": stoichiometric/residual loss,
            "L_bounds": physical bound penalty,
            "L_phase_sum": phase-sum validity loss,
        }

    These can be combined as:
        L_total = alpha * L_data + beta * L_stoich + gamma * L_bounds + delta * L_phase_sum

    Args:
        predicted_phases: Predicted phase fractions.
        input_oxides: Input oxide composition (optional, for stoichiometric loss).
        phase_bounds: Custom phase bounds (optional).

    Returns:
        Dictionary of loss component names and scalar values.

    Notes:
        - This function does NOT compute the ML prediction loss (L_data).
        - Loss values are always non-negative.
        - Use in a PIML loss function during neural network training.
    """
    loss_components = {}

    # Stoichiometric loss
    if input_oxides is not None:
        residual_result = calculate_stoichiometric_residual(input_oxides, predicted_phases)
        # RMS residual is already computed; normalize to [0, ∞)
        loss_components["L_stoich"] = residual_result.get("root_mean_square_residual", 0.0)
    else:
        loss_components["L_stoich"] = 0.0

    # Bound penalty
    bound_result = calculate_physical_bound_penalty(predicted_phases, phase_bounds)
    loss_components["L_bounds"] = bound_result["penalty"]

    # Phase-sum penalty
    phase_sum_result = calculate_phase_sum_residual(predicted_phases)
    loss_components["L_phase_sum"] = 0.0 if phase_sum_result["valid"] else 1.0

    return loss_components
