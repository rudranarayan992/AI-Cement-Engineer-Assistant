"""Deterministic raw-mix engineering scenario analysis.

This module is deliberately limited to raw-material assay -> raw-mix recipe ->
calculated raw-meal chemistry comparisons and sensitivity analysis. It never
claims clinker-quality prediction, nor does it infer Bogue-derived phases or
Free CaO from a raw mix.

The engineering outputs are labeled as CALCULATED OUTPUT and the source raw
materials remain MEASURED INPUT. All scenario computations are deterministic and
traceable.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple

import pandas as pd

from src.chemistry.raw_mix import compute_moduli, compute_weighted_oxides, ignited_basis, mass_balance_sum

DEFAULT_RAW_MATERIALS_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "raw_materials" / "raw_materials_database.csv"
)
DEFAULT_BASELINE_RECIPE = {
    "LS_001": 78.0,
    "CLAY_001": 14.0,
    "SAND_001": 5.0,
    "IRON_001": 3.0,
}
REQUIRED_OXIDES = ["CaO", "SiO2", "Al2O3", "Fe2O3", "MgO", "SO3", "LOI"]
VALID_BASES = {"as_received", "dry", "ignited"}


def _as_float(value: Any, *, field_name: str = "value") -> float:
    if value is None:
        raise ValueError(f"{field_name} is missing")
    try:
        num = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} is not numeric: {value!r}")
    if math.isnan(num) or math.isinf(num):
        raise ValueError(f"{field_name} is not finite: {value!r}")
    return num


def _coerce_materials_frame(materials: Any) -> pd.DataFrame:
    if isinstance(materials, pd.DataFrame):
        df = materials.copy()
    elif isinstance(materials, Mapping):
        if all(isinstance(v, Mapping) for v in materials.values()):
            df = pd.DataFrame.from_dict(materials, orient="index")
        else:
            df = pd.DataFrame(materials)
    else:
        raise TypeError("materials must be a pandas DataFrame or mapping of material_id -> chemistry")

    if df.empty:
        raise ValueError("materials DataFrame is empty")

    if "Sample_ID" in df.columns:
        if "Material_ID" not in df.columns:
            df = df.rename(columns={"Sample_ID": "Material_ID"})
    if "Material_ID" in df.columns:
        df = df.set_index("Material_ID")
    elif "Sample_ID" in df.index.names:
        df.index.name = "Material_ID"

    for oxide in REQUIRED_OXIDES:
        if oxide not in df.columns:
            raise ValueError(f"Materials table is missing required chemistry column: {oxide}")
        df[oxide] = pd.to_numeric(df[oxide], errors="coerce")

    return df


def _normalise_proportions(proportions: Mapping[str, float]) -> Dict[str, float]:
    if not isinstance(proportions, Mapping) or not proportions:
        raise ValueError("proportions must be a non-empty mapping of material_id -> percentage")

    normalized: Dict[str, float] = {}
    for material_id, percentage in proportions.items():
        key = str(material_id)
        value = _as_float(percentage, field_name=f"Material '{key}' proportion")
        if value < 0:
            raise ValueError(f"Material '{key}' has a negative proportion: {value}")
        if math.isnan(value) or math.isinf(value):
            raise ValueError(f"Material '{key}' has invalid proportion: {value}")
        normalized[key] = value
    return normalized


def validate_raw_mix_recipe(
    materials: Any,
    proportions: Mapping[str, float],
    *,
    basis: str = "as_received",
    tolerance: float = 1.0,
) -> Dict[str, Any]:
    """Validate a raw-mix recipe and its chemistry inputs.

    Returns a structured result with `valid`, `errors`, `warnings`, `total`, and
    metadata. Missing chemistry is not silently replaced with zero.
    """
    result: Dict[str, Any] = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "total": 0.0,
        "basis": basis,
        "tolerance": tolerance,
    }

    if basis not in VALID_BASES:
        result["errors"].append(f"Invalid basis '{basis}'. Supported bases: {sorted(VALID_BASES)}")
        return result

    try:
        df = _coerce_materials_frame(materials)
    except Exception as exc:  # pragma: no cover - defensive branch
        result["errors"].append(str(exc))
        return result

    try:
        normalized = _normalise_proportions(proportions)
    except Exception as exc:
        result["errors"].append(str(exc))
        return result

    result["total"] = sum(normalized.values())
    if abs(result["total"] - 100.0) > tolerance:
        result["errors"].append(
            f"Proportion sum {result['total']:.3f}% is outside the permitted tolerance of ±{tolerance}% from 100%"
        )

    for material_id, proportion in normalized.items():
        if material_id not in df.index:
            result["errors"].append(f"Material '{material_id}' not found in input chemistry table")
            continue

        for oxide in REQUIRED_OXIDES:
            value = df.at[material_id, oxide]
            if pd.isna(value):
                result["errors"].append(
                    f"Missing required chemistry for material '{material_id}' oxide '{oxide}'"
                )
                continue
            if not math.isfinite(float(value)):
                result["errors"].append(
                    f"Non-finite chemistry for material '{material_id}' oxide '{oxide}': {value!r}"
                )
                continue
            if float(value) < 0:
                result["errors"].append(
                    f"Negative oxide value for material '{material_id}' oxide '{oxide}': {value}"
                )
            if float(value) > 100.0:
                result["errors"].append(
                    f"Chemistry value for material '{material_id}' oxide '{oxide}' exceeds 100%: {value}"
                )

    if not result["errors"]:
        result["valid"] = True

    return result


def _default_source_dataset() -> str:
    return str(DEFAULT_RAW_MATERIALS_PATH)


def _calculate_moduli_from_oxides(oxide_map: Mapping[str, float], *, basis: str) -> Dict[str, float]:
    if basis == "ignited":
        oxides = dict(oxide_map)
    else:
        oxides = dict(oxide_map)
    moduli = compute_moduli(oxides)
    return {key: float(value) for key, value in moduli.items() if value is not None and math.isfinite(float(value))}


def calculate_raw_mix_scenario(
    materials: Any,
    proportions: Mapping[str, float],
    *,
    basis: str = "as_received",
    source_dataset: Optional[str] = None,
    tolerance: float = 1.0,
    calculation_method: str = "weighted oxide mass balance",
) -> Dict[str, Any]:
    """Calculate a deterministic raw-mix chemistry scenario.

    The return value always contains structured validation metadata. When the
    recipe is invalid, the result remains explicit and contains errors instead of
    silently generating zero-filled values.
    """
    source_file = source_dataset or _default_source_dataset()
    validation = validate_raw_mix_recipe(materials, proportions, basis=basis, tolerance=tolerance)

    result: Dict[str, Any] = {
        "valid": validation["valid"],
        "errors": validation["errors"],
        "warnings": validation["warnings"],
        "basis": basis,
        "tolerance": tolerance,
        "recipe": {},
        "chemistry": {},
        "moduli": {},
        "provenance": {
            "source_material_ids": [],
            "source_dataset": source_file,
            "recipe": {},
            "basis": basis,
            "calculation_method": calculation_method,
            "calculation_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "data_status": "CALCULATED OUTPUT",
            "input_data_status": "MEASURED INPUT",
        },
    }

    if not validation["valid"]:
        return result

    df = _coerce_materials_frame(materials)
    normalized = _normalise_proportions(proportions)
    result["recipe"] = {k: float(v) for k, v in normalized.items()}
    result["provenance"]["source_material_ids"] = list(normalized.keys())
    result["provenance"]["recipe"] = {k: float(v) for k, v in normalized.items()}

    weighted_oxides = compute_weighted_oxides(df, normalized)
    oxides = dict(weighted_oxides)

    if basis == "ignited":
        try:
            oxides, _ = ignited_basis(oxides)
        except ValueError as exc:
            result["errors"].append(f"Ignited-basis conversion failed: {exc}")
            result["valid"] = False
            return result
    elif basis == "dry":
        if "moisture" not in df.columns and "Moisture" not in df.columns:
            result["warnings"].append("Dry-basis requested but no moisture column was provided; returning as-received chemistry")
        else:
            moisture_col = "moisture" if "moisture" in df.columns else "Moisture"
            material_moistures = [float(df.at[mat, moisture_col]) for mat in normalized if mat in df.index and not pd.isna(df.at[mat, moisture_col])]
            if material_moistures:
                overall_moisture = sum(normalized[m] * float(df.at[m, moisture_col]) for m in normalized if m in df.index and not pd.isna(df.at[m, moisture_col])) / 100.0
                if 0.0 <= overall_moisture < 100.0:
                    dry_multiplier = 1.0 / (1.0 - overall_moisture / 100.0)
                    oxides = {k: float(v) * dry_multiplier if k in REQUIRED_OXIDES and not pd.isna(v) else float(v) for k, v in weighted_oxides.items()}
                    oxides["moisture"] = 0.0

    if not all(oxide in oxides for oxide in REQUIRED_OXIDES):
        missing = [oxide for oxide in REQUIRED_OXIDES if oxide not in oxides]
        result["errors"].append(f"Chemistry calculation missing required oxides: {missing}")
        result["valid"] = False
        return result

    for oxide in REQUIRED_OXIDES:
        value = oxides.get(oxide)
        if value is None or pd.isna(value):
            result["errors"].append(f"Calculated chemistry contains missing oxide '{oxide}'")
            result["valid"] = False
            return result
        if not math.isfinite(float(value)):
            result["errors"].append(f"Calculated oxide '{oxide}' is not finite: {value!r}")
            result["valid"] = False
            return result
        if float(value) < 0:
            result["errors"].append(f"Calculated oxide '{oxide}' is negative: {value}")
            result["valid"] = False
            return result

    result["chemistry"] = {oxide: float(oxides[oxide]) for oxide in REQUIRED_OXIDES}
    result["moduli"] = _calculate_moduli_from_oxides(result["chemistry"], basis=basis)
    result["mass_balance_sum"] = float(mass_balance_sum(result["chemistry"]))
    result["mass_balance_ok"] = bool(abs(result["mass_balance_sum"] - 100.0) <= tolerance)
    result["valid"] = True
    return result


def compare_scenarios(
    baseline: Mapping[str, Any],
    scenario: Mapping[str, Any],
    *,
    metrics: Sequence[str] = ("CaO", "SiO2", "Al2O3", "Fe2O3", "MgO", "LSF", "SM", "AM"),
) -> Dict[str, Any]:
    """Compare a baseline scenario against a candidate scenario.

    Returns absolute change and percentage-point change for each requested metric.
    """
    comparison: Dict[str, Any] = {
        "baseline": {},
        "scenario": {},
        "changes": {},
    }

    for metric in metrics:
        baseline_value = baseline.get("chemistry", {}).get(metric)
        if baseline_value is None:
            baseline_value = baseline.get("moduli", {}).get(metric)
        scenario_value = scenario.get("chemistry", {}).get(metric)
        if scenario_value is None:
            scenario_value = scenario.get("moduli", {}).get(metric)

        if baseline_value is None or scenario_value is None:
            comparison["changes"][metric] = {
                "absolute_change": None,
                "percentage_point_change": None,
                "baseline_value": baseline_value,
                "scenario_value": scenario_value,
            }
            continue

        absolute_change = float(scenario_value) - float(baseline_value)
        comparison["changes"][metric] = {
            "absolute_change": absolute_change,
            "percentage_point_change": absolute_change,
            "baseline_value": float(baseline_value),
            "scenario_value": float(scenario_value),
        }

    return comparison


def _redistribute_after_change(
    baseline: Mapping[str, float],
    material_id: str,
    delta: float,
) -> Dict[str, float]:
    updated = dict(baseline)
    if material_id not in updated:
        raise KeyError(f"Material '{material_id}' not found in baseline recipe")

    revised_total = float(updated[material_id]) + float(delta)
    if revised_total < 0.0:
        revised_total = 0.0
    updated[material_id] = revised_total

    remainder = 100.0 - revised_total
    others = [m for m in updated if m != material_id]
    other_total = sum(float(updated[m]) for m in others)
    if other_total <= 0:
        raise ValueError(f"Cannot redistribute proportions after changing material '{material_id}' because others sum to zero")

    for m in others:
        updated[m] = float(updated[m]) * (remainder / other_total)
    updated[material_id] = revised_total

    return {k: float(v) for k, v in updated.items()}


def deterministic_sensitivity_analysis(
    materials: Any,
    baseline_recipe: Mapping[str, float],
    *,
    basis: str = "as_received",
    increment_pct: float = 2.0,
    source_dataset: Optional[str] = None,
    tolerance: float = 1.0,
) -> Dict[str, Any]:
    """Deterministic one-factor-at-a-time sensitivity analysis.

    Labels the result explicitly as DETERMINISTIC CHEMISTRY SENSITIVITY and should
    not be interpreted as causal or machine-learning analysis.
    """
    baseline_result = calculate_raw_mix_scenario(
        materials,
        baseline_recipe,
        basis=basis,
        source_dataset=source_dataset,
        tolerance=tolerance,
    )
    if not baseline_result["valid"]:
        return {
            "valid": False,
            "label": "DETERMINISTIC CHEMISTRY SENSITIVITY",
            "errors": baseline_result["errors"],
            "warnings": baseline_result["warnings"],
            "baseline": baseline_result,
        }

    scenarios: List[Dict[str, Any]] = []
    for material_id in baseline_recipe:
        for direction in ("increase", "decrease"):
            delta = float(increment_pct) if direction == "increase" else -float(increment_pct)
            scenario_recipe = _redistribute_after_change(baseline_recipe, material_id, delta)
            scenario_result = calculate_raw_mix_scenario(
                materials,
                scenario_recipe,
                basis=basis,
                source_dataset=source_dataset,
                tolerance=tolerance,
            )
            if not scenario_result["valid"]:
                continue
            change_summary = compare_scenarios(baseline_result, scenario_result)
            scenarios.append({
                "material_id": material_id,
                "direction": direction,
                "increment_pct": float(increment_pct),
                "recipe": scenario_recipe,
                "result": scenario_result,
                "change_summary": change_summary,
                "label": "DETERMINISTIC CHEMISTRY SENSITIVITY",
            })

    return {
        "valid": True,
        "label": "DETERMINISTIC CHEMISTRY SENSITIVITY",
        "baseline": baseline_result,
        "sensitivity_by_material": scenarios,
    }


def check_engineering_constraints(
    scenario: Mapping[str, Any],
    *,
    lsf_min: float,
    lsf_max: float,
    sm_min: float,
    sm_max: float,
    am_min: float,
    am_max: float,
    warning_tolerance: float = 0.05,
) -> Dict[str, Any]:
    """Evaluate scenario against configurable engineering windows.

    Plant-specific limits are explicit inputs. This function returns PASS / WARNING / FAIL.
    """
    if not scenario.get("valid", False):
        return {
            "overall_status": "FAIL",
            "checks": {},
            "errors": scenario.get("errors", []),
        }

    metrics = {
        "LSF": (scenario["moduli"].get("LSF"), lsf_min, lsf_max),
        "SM": (scenario["moduli"].get("SM"), sm_min, sm_max),
        "AM": (scenario["moduli"].get("AM"), am_min, am_max),
    }
    checks: Dict[str, Any] = {}
    statuses: List[str] = []

    for metric_name, (value, lower, upper) in metrics.items():
        if value is None:
            checks[metric_name] = {"status": "FAIL", "value": None, "limit": [lower, upper]}
            statuses.append("FAIL")
            continue

        value_float = float(value)
        if lower <= value_float <= upper:
            status = "PASS"
        else:
            nearest = lower if abs(value_float - lower) <= abs(value_float - upper) else upper
            threshold = max(abs(nearest) * warning_tolerance, 1e-9)
            status = "WARNING" if abs(value_float - nearest) <= threshold else "FAIL"
        checks[metric_name] = {
            "status": status,
            "value": value_float,
            "limit": [lower, upper],
        }
        statuses.append(status)

    overall = "FAIL" if "FAIL" in statuses else "WARNING" if "WARNING" in statuses else "PASS"
    return {
        "overall_status": overall,
        "checks": checks,
        "errors": [],
    }


def rank_feasible_scenarios(
    scenarios: Sequence[Mapping[str, Any]],
    baseline: Mapping[str, Any],
    *,
    lsf_min: float,
    lsf_max: float,
    sm_min: float,
    sm_max: float,
    am_min: float,
    am_max: float,
) -> List[Dict[str, Any]]:
    """Rank user-created recipes by deterministic feasibility and distance from baseline.

    This is not a machine-learning optimizer and it does not claim that highest
    rank guarantees better clinker quality.
    """
    ranked: List[Dict[str, Any]] = []
    for scenario in scenarios:
        if not scenario.get("valid", False):
            continue
        constraint_result = check_engineering_constraints(
            scenario,
            lsf_min=lsf_min,
            lsf_max=lsf_max,
            sm_min=sm_min,
            sm_max=sm_max,
            am_min=am_min,
            am_max=am_max,
        )
        if constraint_result["overall_status"] == "FAIL":
            continue

        delta = compare_scenarios(baseline, scenario)
        distance = 0.0
        for metric in ("CaO", "SiO2", "Al2O3", "Fe2O3", "MgO", "LSF", "SM", "AM"):
            change = delta["changes"].get(metric, {}).get("absolute_change")
            if change is not None:
                distance += float(change) ** 2
        distance = math.sqrt(distance)

        ranked.append({
            "scenario": scenario,
            "constraint_status": constraint_result["overall_status"],
            "distance_from_baseline": distance,
            "rank_score": distance,
        })

    ranked.sort(key=lambda item: (item["rank_score"], item["constraint_status"]))
    return ranked


def build_baseline_scenario(
    materials: Any,
    *,
    recipe: Optional[Mapping[str, float]] = None,
    source_dataset: Optional[str] = None,
    basis: str = "as_received",
    tolerance: float = 1.0,
) -> Dict[str, Any]:
    return calculate_raw_mix_scenario(
        materials,
        recipe or DEFAULT_BASELINE_RECIPE,
        basis=basis,
        source_dataset=source_dataset,
        tolerance=tolerance,
    )
