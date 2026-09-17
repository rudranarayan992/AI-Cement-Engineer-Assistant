"""End-to-end cement process analytics pipeline using repository data only.

This module is intentionally limited to deterministic engineering analytics and
provenance tracking. It does not train any model and does not pretend that the
synthetic or reference calculations are measured production targets.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd

from src.features.chemistry_features import extract_cement_chemistry_features


DEFAULT_DATASET_FILES = {
    "raw_materials": "raw_materials/raw_materials_database.csv",
    "raw_meal": "raw_mix/raw_meal_samples.csv",
    "kiln_telemetry": "kiln_process/kiln_telemetry.csv",
    "clinker_analysis": "clinker/clinker_analysis.csv",
    "cement_quality": "cement/cement_quality.csv",
}


def _resolve_data_dir(data_dir: Optional[str | Path] = None) -> Path:
    if data_dir is None:
        return Path(__file__).resolve().parents[1] / "data"
    return Path(data_dir)


def load_cement_process_tables(data_dir: Optional[str | Path] = None) -> Dict[str, pd.DataFrame]:
    """Load the repository's cement-process tables from disk.

    Returns a dictionary keyed by the stage name. Each DataFrame preserves the
    real repository schema and values without synthetic augmentation.
    """
    base_dir = _resolve_data_dir(data_dir)
    datasets: Dict[str, pd.DataFrame] = {}
    missing: List[str] = []

    for name, rel_path in DEFAULT_DATASET_FILES.items():
        path = base_dir / rel_path
        if not path.exists():
            missing.append(str(path))
            continue
        datasets[name] = pd.read_csv(path)

    if missing:
        raise FileNotFoundError(f"Missing required dataset files: {missing}")

    return datasets


def _rename_raw_meal_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "Raw_CaO": "CaO",
        "Raw_SiO2": "SiO2",
        "Raw_Al2O3": "Al2O3",
        "Raw_Fe2O3": "Fe2O3",
        "Raw_MgO": "MgO",
        "Raw_SO3": "SO3",
    }
    renamed = df.copy()
    return renamed.rename(columns=rename_map)


def _rename_clinker_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "Clinker_CaO": "CaO",
        "Clinker_SiO2": "SiO2",
        "Clinker_Al2O3": "Al2O3",
        "Clinker_Fe2O3": "Fe2O3",
        "Free_CaO_pct": "Free_CaO",
        "C3S_pct": "C3S",
        "C2S_pct": "C2S",
        "C3A_pct": "C3A",
        "C4AF_pct": "C4AF",
    }
    renamed = df.copy()
    return renamed.rename(columns=rename_map)


def _rename_cement_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "Strength_28d_MPa": "Strength_28d_MPa",
        "Gypsum_SO3_pct": "Gypsum_SO3_pct",
        "Blaine_cm2g": "Blaine_cm2g",
    }
    renamed = df.copy()
    return renamed.rename(columns=rename_map)


def build_cement_process_dataframe(data_dir: Optional[str | Path] = None) -> pd.DataFrame:
    """Merge the real process tables and attach chemistry features.

    The pipeline intentionally uses only the repository's cement-process data and
    keeps all values at their actual measurement basis. Bogue calculations are
    retained as reference values, not as measured phase labels.
    """
    tables = load_cement_process_tables(data_dir)

    raw_meal = _rename_raw_meal_columns(tables["raw_meal"])
    clinker = _rename_clinker_columns(tables["clinker_analysis"])
    kiln = tables["kiln_telemetry"].copy()
    cement = _rename_cement_columns(tables["cement_quality"])

    merged = raw_meal.merge(clinker, on="Batch_ID", how="inner")
    merged = merged.merge(kiln, on="Batch_ID", how="left")
    merged = merged.merge(cement, on="Batch_ID", how="left")

    feature_columns = ["lsf", "sm", "am", "bogue_reference_c3s", "bogue_reference_c2s", "bogue_reference_c3a", "bogue_reference_c4af"]
    for col in feature_columns:
        merged[col] = pd.NA

    chemistry_valid = []
    warnings = []

    for idx, row in merged.iterrows():
        batch_id = str(row["Batch_ID"])
        oxide_data = {
            "CaO": row.get("CaO_x", row.get("CaO")),
            "SiO2": row.get("SiO2_x", row.get("SiO2")),
            "Al2O3": row.get("Al2O3_x", row.get("Al2O3")),
            "Fe2O3": row.get("Fe2O3_x", row.get("Fe2O3")),
            "MgO": row.get("MgO"),
            "SO3": row.get("SO3"),
            "LOI": row.get("LOI"),
        }

        free_cao = row.get("Free_CaO")
        feature_set = extract_cement_chemistry_features(
            oxide_data=oxide_data,
            batch_id=batch_id,
            input_basis="as_received",
            free_cao=free_cao,
            so3=row.get("SO3"),
        )

        chemistry_valid.append(bool(feature_set.computation_valid))
        warnings.append(feature_set.warnings)

        for col in feature_columns:
            if col == "lsf":
                merged.at[idx, col] = feature_set.lsf
            elif col == "sm":
                merged.at[idx, col] = feature_set.sm
            elif col == "am":
                merged.at[idx, col] = feature_set.am
            elif col == "bogue_reference_c3s":
                merged.at[idx, col] = feature_set.bogue_reference_c3s
            elif col == "bogue_reference_c2s":
                merged.at[idx, col] = feature_set.bogue_reference_c2s
            elif col == "bogue_reference_c3a":
                merged.at[idx, col] = feature_set.bogue_reference_c3a
            elif col == "bogue_reference_c4af":
                merged.at[idx, col] = feature_set.bogue_reference_c4af

    merged["chemistry_valid"] = chemistry_valid
    merged["synthetic_target"] = False
    merged["data_status"] = "real_repository_data_only"
    merged["warnings"] = warnings
    return merged


def build_cement_process_pipeline(data_dir: Optional[str | Path] = None) -> Dict[str, Any]:
    """Return the deterministic process analytics summary for the repository chain."""
    df = build_cement_process_dataframe(data_dir)
    valid_batches = int(df["chemistry_valid"].sum()) if "chemistry_valid" in df.columns else 0
    total_batches = len(df)

    numeric_cols = ["lsf", "sm", "am", "bogue_reference_c3s", "bogue_reference_c2s", "bogue_reference_c3a", "bogue_reference_c4af"]
    feature_stats = {}
    for col in numeric_cols:
        if col in df.columns:
            values = pd.to_numeric(df[col], errors="coerce")
            feature_stats[col] = {
                "mean": float(values.mean()) if values.notna().any() else None,
                "min": float(values.min()) if values.notna().any() else None,
                "max": float(values.max()) if values.notna().any() else None,
            }

    strength_28d = pd.to_numeric(df.get("Strength_28d_MPa", pd.Series(dtype=float)), errors="coerce")
    kiln_temp = pd.to_numeric(df.get("Kiln_Temp_C", pd.Series(dtype=float)), errors="coerce")
    feed_rate = pd.to_numeric(df.get("Feed_Rate_tph", pd.Series(dtype=float)), errors="coerce")

    summary = {
        "project": "AI Cement Project",
        "pipeline_type": "engineering_analytics_only",
        "data_source": "real_repository_csvs",
        "synthetic_targets_detected": False,
        "total_batches": total_batches,
        "valid_chemistry_batches": valid_batches,
        "chemistry_validity_rate": float(valid_batches / total_batches) if total_batches else 0.0,
        "feature_summary": feature_stats,
        "mean_28d_strength_mpa": float(strength_28d.mean()) if strength_28d.notna().any() else None,
        "mean_kiln_temp_c": float(kiln_temp.mean()) if kiln_temp.notna().any() else None,
        "mean_feed_rate_tph": float(feed_rate.mean()) if feed_rate.notna().any() else None,
        "restriction": "No model training; no synthetic labels; no concrete/cement merge.",
    }

    return {
        "dataset": df,
        "summary": summary,
        "source_files": {name: str(_resolve_data_dir(data_dir) / rel) for name, rel in DEFAULT_DATASET_FILES.items()},
    }
