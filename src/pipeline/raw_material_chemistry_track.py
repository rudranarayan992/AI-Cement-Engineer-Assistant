"""Track C: raw-material -> raw-meal chemistry validation only.

This module stays within the valid chemistry-only workflow defined for Step 12K:
raw material assay -> raw mix recipe -> weighted raw-meal chemistry -> LSF/SM/AM
validation.

Important constraints:
- This is not a clinker prediction model.
- This does not create a clinker target or phase label.
- All output is explicitly marked as calculated metadata, never measured production data.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, MutableMapping, Optional

import pandas as pd

from src.chemistry.chemistry_engine import calculate_raw_mix_chemistry
from src.validation.physics_constraints import validate_all

DEFAULT_RAW_MATERIALS_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "raw_materials" / "raw_materials_database.csv"
)
DEFAULT_RESULT_PATH = Path(__file__).resolve().parents[2] / "results" / "track_c_raw_meal_calculated.csv"

DEFAULT_RAW_MEAL_RECIPE = {
    "LS_001": 78.0,
    "CLAY_001": 14.0,
    "SAND_001": 5.0,
    "IRON_001": 3.0,
}


def load_raw_material_library(csv_path: str | Path = DEFAULT_RAW_MATERIALS_PATH) -> pd.DataFrame:
    """Load the repository's raw material assay table.

    The imported table is treated as a measured raw-material library. The derived
    raw-meal output is calculated from this library and labeled as `calculated`.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Raw material library not found: {path}")

    df = pd.read_csv(path)
    required = {"Sample_ID", "Material_Type", "CaO", "SiO2", "Al2O3", "Fe2O3", "MgO", "SO3", "LOI"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Raw material library is missing required columns: {missing}")
    return df


def _normalise_mix_proportions(mix_proportions: Optional[Mapping[str, float]]) -> Dict[str, float]:
    if mix_proportions is None:
        mix_proportions = DEFAULT_RAW_MEAL_RECIPE
    normalized = {str(k): float(v) for k, v in dict(mix_proportions).items()}
    if not normalized:
        raise ValueError("mix_proportions must contain at least one material.")
    total = sum(normalized.values())
    if total <= 0:
        raise ValueError("mix_proportions must sum to a positive value.")
    return normalized


def build_calculated_raw_meal(
    raw_materials_csv: str | Path = DEFAULT_RAW_MATERIALS_PATH,
    mix_proportions: Optional[Mapping[str, float]] = None,
    basis: str = "as_received",
) -> Dict[str, Any]:
    """Calculate a derived raw-meal chemistry record from measured material assays.

    The output is intentionally marked as `calculated` and is limited to the valid
    raw-material -> raw-meal chemistry track. It does not generate a clinker target.
    """
    materials = load_raw_material_library(raw_materials_csv)
    normalized_mix = _normalise_mix_proportions(mix_proportions)

    sample_ids = set(materials["Sample_ID"].astype(str))
    missing_materials = sorted(k for k in normalized_mix if k not in sample_ids)
    if missing_materials:
        raise KeyError(f"The following materials are missing from the raw material table: {missing_materials}")

    materials_indexed = materials.set_index("Sample_ID")
    chemistry = calculate_raw_mix_chemistry(materials_indexed, normalized_mix, basis=basis)
    validation = validate_all(
        raw_mix_proportions={k: float(v) for k, v in normalized_mix.items()},
        input_oxides={k: float(v) for k, v in chemistry["oxides"].items() if pd.notna(v)},
    )

    oxide_data = {k: float(v) for k, v in chemistry["oxides"].items() if pd.notna(v)}
    validation_moduli = validation.get("checks", {}).get("moduli", {})

    result: Dict[str, Any] = {
        "track": "12K_raw_material_to_raw_meal_chemistry",
        "data_status": "calculated",
        "scientific_scope": "raw_material_assay -> raw_mix_recipe -> calculated_raw_meal_chemistry",
        "restriction": "This output is chemistry-only, not clinker prediction, not clinker target training.",
        "basis": basis,
        "mix_proportions": normalized_mix,
        "weighted_oxide_composition_pct": oxide_data,
        "moduli": {
            "LSF": float(chemistry.get("LSF", float("nan"))),
            "SM": float(chemistry.get("SM", float("nan"))),
            "AM": float(chemistry.get("AM", float("nan"))),
        },
        "moduli_validation": validation_moduli,
        "mass_balance_sum": float(chemistry.get("mass_balance_sum", float("nan"))),
        "mass_balance_ok": bool(chemistry.get("mass_balance_ok", False)),
        "validation": validation,
    }
    return result


def export_calculated_raw_meal_csv(
    output_csv: str | Path = DEFAULT_RESULT_PATH,
    raw_materials_csv: str | Path = DEFAULT_RAW_MATERIALS_PATH,
    mix_proportions: Optional[Mapping[str, float]] = None,
    basis: str = "as_received",
) -> pd.DataFrame:
    """Persist the calculated raw-meal chemistry as a separate derived CSV.

    The output is intentionally written to a results file rather than modifying the
    source raw-material database or the synthetic raw-meal samples.
    """
    result = build_calculated_raw_meal(raw_materials_csv=raw_materials_csv, mix_proportions=mix_proportions, basis=basis)
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    row: Dict[str, Any] = {
        "track": result["track"],
        "data_status": result["data_status"],
        "scientific_scope": result["scientific_scope"],
        "basis": result["basis"],
        "mix_total_pct": round(sum(result["mix_proportions"].values()), 6),
        "LSF": result["moduli"]["LSF"],
        "SM": result["moduli"]["SM"],
        "AM": result["moduli"]["AM"],
        "mass_balance_sum": result["mass_balance_sum"],
        "mass_balance_ok": result["mass_balance_ok"],
    }
    for oxide_name, oxide_value in result["weighted_oxide_composition_pct"].items():
        row[f"{oxide_name}_pct"] = oxide_value
    for material_id, proportion in result["mix_proportions"].items():
        row[f"{material_id}_pct"] = proportion

    df = pd.DataFrame([row])
    df.to_csv(output_path, index=False)
    return df
