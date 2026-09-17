"""Scientific data-acceptance checks for plant-linked clinker datasets.

This module is intentionally narrow: it validates whether a supplied clinker dataset
is qualified for the main industrial research track. It does not repair data or
convert invalid values into valid values. Any bad scientific dataset is reported as
FAIL or WARNING with explicit reasons.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd


OXIDE_COLUMNS = [
    "CaO_wt_pct",
    "SiO2_wt_pct",
    "Al2O3_wt_pct",
    "Fe2O3_wt_pct",
    "MgO_wt_pct",
    "SO3_wt_pct",
    "Na2O_wt_pct",
    "K2O_wt_pct",
    "LOI_wt_pct",
]

PHASE_COLUMNS = ["C3S_pct", "C2S_pct", "C3A_pct", "C4AF_pct"]
REQUIRED_COLUMNS = [
    "Sample_ID",
    "Plant_ID",
    "Kiln_ID",
    "Production_DateTime",
    "Sampling_DateTime",
    "Raw_Mix_ID",
    "Kiln_Run_ID",
    "Free_CaO_pct",
    *OXIDE_COLUMNS,
    "Phase_Method",
    "Oxide_Method",
    "Free_CaO_Method",
    "Lab_ID",
    "Instrument_ID",
    "Measurement_DateTime",
    "Replicate_ID",
    "Units",
    "Basis",
]


def _as_datetime(value: Any) -> Optional[pd.Timestamp]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, pd.Timestamp):
        ts = value
    else:
        try:
            ts = pd.to_datetime(value, errors="raise")
        except Exception:
            return None
    if pd.isna(ts):
        return None
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert("UTC")


def _status_from_reasons(reasons: Iterable[str]) -> str:
    reasons = list(reasons)
    if not reasons:
        return "PASS"
    if any("FAIL" in reason.upper() for reason in reasons):
        return "FAIL"
    return "WARNING"


def _record_reason(reasons: List[str], category: str, message: str) -> None:
    reasons.append(f"{category}: {message}")


def validate_clinker_dataset(
    df: pd.DataFrame,
    *,
    provenance: Optional[Dict[str, Any]] = None,
    traceability: Optional[Dict[str, Any]] = None,
    reference_time: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Validate a clinker dataset for research-readiness.

    Returns a structured dictionary containing the overall status, explicit reasons,
    and a per-check summary. This function is intentionally strict and does not
    silently coerce invalid data.
    """
    if df is None or df.empty:
        return {
            "status": "FAIL",
            "reasons": ["FAIL: dataset is empty or missing"],
            "checks": {"rows": 0, "columns": 0},
            "n_rows": 0,
            "n_unique_samples": 0,
        }

    reasons: List[str] = []
    checks: Dict[str, Any] = {
        "missing_columns": [],
        "duplicate_sample_ids": [],
        "missing_time_fields": [],
        "invalid_timestamps": [],
        "oxide_issues": [],
        "free_cao_issues": [],
        "phase_issues": [],
        "provenance_issues": [],
        "traceability_issues": [],
        "measurement_issues": [],
    }

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        checks["missing_columns"] = missing_columns
        for col in missing_columns:
            _record_reason(reasons, "FAIL", f"Required column missing: {col}")

    n_rows = len(df)
    n_unique_samples = df["Sample_ID"].nunique() if "Sample_ID" in df.columns else 0
    duplicate_ids = df["Sample_ID"][df["Sample_ID"].duplicated(keep=False)]
    if not duplicate_ids.empty:
        duplicate_ids = sorted(set(pd.Series(duplicate_ids).astype(str).tolist()))
        checks["duplicate_sample_ids"] = duplicate_ids
        for sample_id in duplicate_ids:
            _record_reason(reasons, "FAIL", f"Duplicate Sample_ID detected: {sample_id}")

    for field in ["Sample_ID", "Plant_ID", "Kiln_ID", "Production_DateTime", "Sampling_DateTime", "Raw_Mix_ID", "Kiln_Run_ID"]:
        if field in df.columns:
            missing = df[field].isna() | df[field].astype(str).str.strip().eq("")
            if missing.any():
                bad = df.loc[missing, field].astype(str).tolist()[:5]
                checks["missing_time_fields" if "DateTime" in field else "measurement_issues"].append({field: bad})
                _record_reason(reasons, "FAIL", f"Missing or blank value in required field: {field}")

    for field in ["Production_DateTime", "Sampling_DateTime", "Measurement_DateTime"]:
        if field in df.columns:
            bad = []
            for index, value in df[field].items():
                dt = _as_datetime(value)
                if dt is None:
                    bad.append({index: value})
            if bad:
                checks["invalid_timestamps"].extend(bad)
                _record_reason(reasons, "FAIL", f"Invalid timestamp field detected: {field}")

    if reference_time is None:
        reference_time = pd.Timestamp(datetime.now(timezone.utc))
    else:
        reference_time = pd.Timestamp(reference_time)
        if reference_time.tzinfo is None:
            reference_time = reference_time.tz_localize("UTC")
        else:
            reference_time = reference_time.tz_convert("UTC")

    for field in ["Production_DateTime", "Sampling_DateTime", "Measurement_DateTime"]:
        if field in df.columns:
            future_rows = []
            for index, value in df[field].items():
                dt = _as_datetime(value)
                if dt is not None:
                    if dt > reference_time + pd.Timedelta(days=7):
                        future_rows.append({index: value})
            if future_rows:
                checks["invalid_timestamps"].extend(future_rows)
                _record_reason(reasons, "WARNING", f"Suspicious future information in {field}")

    for oxide in OXIDE_COLUMNS:
        if oxide not in df.columns:
            continue
        values = pd.to_numeric(df[oxide], errors="coerce")
        bad = values[(values < 0) | (values > 100)].index.tolist()
        if bad:
            checks["oxide_issues"].append({oxide: bad})
            _record_reason(reasons, "FAIL", f"Impossible oxide value detected for {oxide}")

    if "Free_CaO_pct" in df.columns:
        values = pd.to_numeric(df["Free_CaO_pct"], errors="coerce")
        bad = values[values < 0].index.tolist()
        if bad:
            checks["free_cao_issues"].append({"Free_CaO_pct": bad})
            _record_reason(reasons, "FAIL", "Negative Free CaO detected")

    if any(col in df.columns for col in PHASE_COLUMNS):
        phase_cols = [col for col in PHASE_COLUMNS if col in df.columns]
        phase_subset = df[phase_cols].apply(pd.to_numeric, errors="coerce")
        for idx, row in phase_subset.iterrows():
            if row.isna().all():
                continue
            if any(pd.isna(v) for v in row.tolist()):
                _record_reason(reasons, "WARNING", f"Missing phase fraction in row {idx}")
                continue
            total = float(row.sum())
            invalid_rows = [
                v for v in row.tolist() if (pd.isna(v) or v < 0 or v > 100)
            ]
            if invalid_rows:
                _record_reason(reasons, "FAIL", f"Invalid phase fraction value in row {idx}")
                continue
            if total < 80.0 or total > 120.0:
                _record_reason(reasons, "FAIL", f"Phase sum problem for row {idx}: total={total:.2f}%")
            elif abs(total - 100.0) > 10.0:
                _record_reason(reasons, "WARNING", f"Phase total is outside a normal 100% window for row {idx}: total={total:.2f}%")

    for field in ["Phase_Method", "Oxide_Method", "Free_CaO_Method", "Units", "Basis"]:
        if field in df.columns:
            missing = df[field].isna() | df[field].astype(str).str.strip().eq("")
            if missing.any():
                _record_reason(reasons, "FAIL", f"Missing measurement or metadata field: {field}")
                checks["measurement_issues"].append({field: int(missing.sum())})

    if provenance is None:
        provenance = {}
    provenance_required = ["Lab_ID", "Instrument_ID", "Measurement_DateTime", "Replicate_ID"]
    for key in provenance_required:
        if key not in provenance and key not in df.columns:
            _record_reason(reasons, "FAIL", f"Missing provenance information: {key}")
            checks["provenance_issues"].append(key)

    if traceability is None:
        traceability = {}
    raw_mix_ids = set(pd.Series(df.get("Raw_Mix_ID", pd.Series([], dtype=object))).dropna().astype(str))
    kiln_run_ids = set(pd.Series(df.get("Kiln_Run_ID", pd.Series([], dtype=object))).dropna().astype(str))
    plant_ids = set(pd.Series(df.get("Plant_ID", pd.Series([], dtype=object))).dropna().astype(str))
    if not raw_mix_ids or not kiln_run_ids or not plant_ids:
        _record_reason(reasons, "FAIL", "Missing traceability linkage (Raw_Mix_ID, Kiln_Run_ID, or Plant_ID)")
        checks["traceability_issues"].append({"raw_mix_ids": list(raw_mix_ids), "kiln_run_ids": list(kiln_run_ids), "plant_ids": list(plant_ids)})
    if traceability:
        for sample_id, info in traceability.items():
            if sample_id not in set(df["Sample_ID"].astype(str)):
                continue
            if not isinstance(info, dict):
                _record_reason(reasons, "FAIL", f"Traceability record for {sample_id} is not a dictionary")
                continue
            required_keys = ["Raw_Mix_ID", "Kiln_Run_ID", "Plant_ID", "Kiln_ID"]
            missing_keys = [k for k in required_keys if not info.get(k)]
            if missing_keys:
                _record_reason(reasons, "FAIL", f"Inconsistent sample linkage for {sample_id}: missing {missing_keys}")
                checks["traceability_issues"].append({"sample_id": sample_id, "missing_keys": missing_keys})

    if not reasons:
        status = "PASS"
    elif any("FAIL" in reason.upper() for reason in reasons):
        status = "FAIL"
    else:
        status = "WARNING"

    return {
        "status": status,
        "reasons": reasons,
        "checks": checks,
        "n_rows": n_rows,
        "n_unique_samples": n_unique_samples,
    }


def validate_clinker_record(record: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
    """Convenience wrapper for a single clinker record."""
    df = pd.DataFrame([record])
    return validate_clinker_dataset(df, **kwargs)
