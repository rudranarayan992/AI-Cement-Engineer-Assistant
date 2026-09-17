"""Raw mix chemistry calculations for AI Cement Engineer Phase 2.

Provides deterministic functions to compute:
- weighted oxide composition from a raw mix
- ignited-basis normalization (LOI correction)
- Lime Saturation Factor (LSF), Silica Modulus (SM), Alumina Modulus (AM)
- simple mass-balance checks
- Bogue theoretical phase estimates (optional)

All functions use percent units for oxide compositions (0-100 scale) and
fractions for mix proportions (0-1) or percent (0-100).

These functions are deterministic and do not invent measured data.
"""
from typing import Dict, Iterable, Tuple
import math
import pandas as pd

OXIDE_COLUMNS = [
    "CaO",
    "SiO2",
    "Al2O3",
    "Fe2O3",
    "MgO",
    "SO3",
    "Na2O",
    "K2O",
    "TiO2",
    "P2O5",
    "LOI",
]


def _to_fraction_dict(proportions: Dict[str, float]) -> Dict[str, float]:
    """Convert a dict of proportions (either sum-to-1 fractions or sum-to-100 percents)
    into fractions summing to 1. Raises ValueError for invalid inputs.
    """
    keys = list(proportions.keys())
    vals = [float(proportions[k]) for k in keys]
    s = sum(vals)
    if s == 0:
        raise ValueError("Sum of proportions is zero")
    # If they look like percents (sum approx 100), convert to fractions
    if abs(s - 100.0) < 1.0:  # tolerant threshold
        return {k: v / 100.0 for k, v in zip(keys, vals)}
    # If they already sum to ~1
    if abs(s - 1.0) < 1e-6 or s <= 1.0 + 1e-6:
        return {k: v / s for k, v in zip(keys, vals)}
    # Otherwise normalize to fractions
    return {k: v / s for k, v in zip(keys, vals)}


def compute_weighted_oxides(materials_df: pd.DataFrame, mix_proportions: Dict[str, float]) -> Dict[str, float]:
    """Compute weighted oxide composition of a raw mix.

    materials_df: DataFrame indexed by Material_ID or with column 'Material_ID'.
    The DataFrame must contain oxide columns in percent units (0-100) or NaN for missing.

    mix_proportions: mapping Material_ID -> fraction (0-1) or percent (0-100).

    Returns dict of oxide_name -> weighted percent (raw, unignited).
    Missing oxide values are ignored in the weighted average (equivalent to treating as NA).
    """
    df = materials_df.copy()
    if "Material_ID" in df.columns:
        df = df.set_index("Material_ID")
    fracs = _to_fraction_dict(mix_proportions)

    # Ensure materials exist
    for mat in fracs.keys():
        if mat not in df.index:
            raise KeyError(f"Material_ID '{mat}' not found in materials_df")

    result = {}
    # compute weighted sums for oxide columns
    for oxide in OXIDE_COLUMNS:
        wt_sum = 0.0
        total_weight = 0.0
        for mat, frac in fracs.items():
            val = df.at[mat, oxide] if oxide in df.columns else None
            if pd.isna(val) or val is None or str(val).strip() == "":
                continue
            try:
                v = float(val)
            except Exception:
                continue
            wt_sum += frac * v
            total_weight += frac
        # if total_weight==0 then all values missing -> NaN
        result[oxide] = float(wt_sum) if total_weight > 0 else float("nan")

    return result


def ignited_basis(raw_oxides: Dict[str, float]) -> Tuple[Dict[str, float], float]:
    """Convert raw (unignited) oxide percents to ignited-basis (LOI removed).

    Returns (oxide_ignited_dict, multiplier) where multiplier = 1/(1-LOI/100).
    Raises ValueError if LOI is missing or >=100.
    """
    LOI = raw_oxides.get("LOI")
    if LOI is None or (isinstance(LOI, float) and math.isnan(LOI)):
        raise ValueError("LOI must be provided for ignited basis conversion")
    LOI = float(LOI)
    if LOI >= 100.0:
        raise ValueError("LOI must be less than 100")
    multiplier = 1.0 / (1.0 - LOI / 100.0)
    ign = {}
    for k, v in raw_oxides.items():
        if v is None:
            ign[k] = float("nan")
            continue
        try:
            num = float(v)
        except Exception:
            ign[k] = float("nan")
            continue
        if k == "LOI":
            ign[k] = v
        else:
            ign[k] = num * multiplier
    return ign, multiplier


def compute_moduli(oxide_ign: Dict[str, float]) -> Dict[str, float]:
    """Compute LSF, SM, AM from ignited-basis oxide percents.

    Expects keys: 'CaO', 'SiO2', 'Al2O3', 'Fe2O3'. Values in percent (0-100).
    Returns dict with 'LSF','SM','AM' (LSF in percent scale e.g., 95.0 means 95%).
    """
    try:
        CaO = float(oxide_ign.get("CaO", 0.0))
        SiO2 = float(oxide_ign.get("SiO2", 0.0))
        Al2O3 = float(oxide_ign.get("Al2O3", 0.0))
        Fe2O3 = float(oxide_ign.get("Fe2O3", 0.0))
    except Exception as e:
        raise ValueError(f"Invalid oxide values: {e}")

    denom = 2.8 * SiO2 + 1.18 * Al2O3 + 0.65 * Fe2O3
    lsf = (CaO / denom) * 100.0 if denom != 0 else float("nan")
    sm = (SiO2 / (Al2O3 + Fe2O3)) if (Al2O3 + Fe2O3) != 0 else float("nan")
    am = (Al2O3 / Fe2O3) if Fe2O3 != 0 else float("nan")
    return {"LSF": lsf, "SM": sm, "AM": am}


def mass_balance_sum(raw_oxides: Dict[str, float], include: Iterable[str] = None) -> float:
    """Return sum of specified oxides (defaults to main oxides + LOI).

    raw_oxides values are percent numbers.
    """
    if include is None:
        include = ["CaO", "SiO2", "Al2O3", "Fe2O3", "MgO", "SO3", "LOI"]
    s = 0.0
    for k in include:
        v = raw_oxides.get(k)
        try:
            if v is None or (isinstance(v, float) and math.isnan(v)):
                continue
            s += float(v)
        except Exception:
            continue
    return s


def bogue_phases(oxide_ign: Dict[str, float], free_CaO: float = 0.0) -> Dict[str, float]:
    """Compute theoretical Bogue phases from ignited oxide percents.

    free_CaO: percent of free CaO (in same percent units as CaO). Default 0.
    Returns dict: C3S, C2S, C3A, C4AF (percent).
    """
    CaO = float(oxide_ign.get("CaO", 0.0))
    SiO2 = float(oxide_ign.get("SiO2", 0.0))
    Al2O3 = float(oxide_ign.get("Al2O3", 0.0))
    Fe2O3 = float(oxide_ign.get("Fe2O3", 0.0))
    SO3 = float(oxide_ign.get("SO3", 0.0)) if oxide_ign.get("SO3") is not None else 0.0

    C3S = 4.071 * (CaO - free_CaO) - 7.600 * SiO2 - 6.718 * Al2O3 - 1.430 * Fe2O3 - 2.852 * SO3
    C2S = 2.867 * SiO2 - 0.7544 * C3S
    C3A = 2.650 * Al2O3 - 1.692 * Fe2O3
    C4AF = 3.043 * Fe2O3
    return {"C3S": C3S, "C2S": C2S, "C3A": C3A, "C4AF": C4AF}


if __name__ == "__main__":
    # quick smoke demo using the illustrative RM001/RM002 example from project notes
    import os
    import json
    base = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
    base = os.path.abspath(base)
    print("raw mix utilities module loaded")
