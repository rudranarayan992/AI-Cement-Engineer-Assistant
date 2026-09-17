"""High-level chemistry engine wrapper for deterministic raw-mix and moduli calculations.

This module provides a stable, validated interface around the existing
`raw_mix` and `clinker_chemistry` utilities. It intentionally does NOT
duplicate low-level formulas; instead it calls the underlying helpers and
adds strict input validation, basis handling and traceable structured outputs.

Public API:
- calculate_raw_mix_chemistry(materials, proportions, basis='as_received')
- calculate_lsf(cao, sio2, al2o3, fe2o3, basis='ignited')
- calculate_sm(sio2, al2o3, fe2o3, basis='ignited')
- calculate_am(al2o3, fe2o3, basis='ignited')

Supported basis: 'as_received', 'dry', 'ignited'

Notes:
- This wrapper will NOT silently convert bases. If you provide oxide numbers
  to `calculate_lsf/sm/am` they are assumed to be already on the requested
  basis; if conversion is required, use `calculate_raw_mix_chemistry` which
  accepts raw materials and proportions and can perform ignited-basis
  conversion when LOI is available.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple

import math
import pandas as pd

try:
    # Preferred package-style imports when used as installed package
    from src.chemistry import raw_mix as _raw_mix  # type: ignore
    from src.chemistry import clinker_chemistry as _clinker  # type: ignore
except Exception:
    try:
        # Relative import if running as part of package
        if __package__:
            from . import raw_mix as _raw_mix  # type: ignore
            from . import clinker_chemistry as _clinker  # type: ignore
        else:
            raise ImportError
    except Exception:
        # Last-resort: load from file path so tests can import the module directly
        import importlib.util
        import os

        base = os.path.dirname(__file__)
        def _load_module(name, fname):
            path = os.path.join(base, fname)
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod

        _raw_mix = _load_module("raw_mix", "raw_mix.py")
        _clinker = _load_module("clinker_chemistry", "clinker_chemistry.py")

SUPPORTED_BASES = {"as_received", "dry", "ignited"}


def _ensure_materials_df(materials: Any) -> pd.DataFrame:
    """Accept a DataFrame or mapping and return a DataFrame indexed by Material_ID.

    The returned frame may contain oxide columns and optional 'LOI' and 'moisture'.
    """
    if isinstance(materials, pd.DataFrame):
        df = materials.copy()
    elif isinstance(materials, dict):
        df = pd.DataFrame.from_dict(materials, orient="index")
        if "Material_ID" not in df.columns:
            df.index.name = "Material_ID"
            df = df.reset_index()
    else:
        raise TypeError("materials must be a pandas.DataFrame or a mapping")

    # Ensure Material_ID index
    if "Material_ID" in df.columns:
        df = df.set_index("Material_ID")

    return df


def calculate_raw_mix_chemistry(
    materials: Any,
    proportions: Dict[str, float],
    basis: str = "as_received",
    tolerance_pct: float = 1.0,
) -> Dict[str, Any]:
    """Compute aggregated raw-meal oxides and moduli with validation and tracing.

    materials: DataFrame (indexed by Material_ID) or mapping Material_ID -> oxide dict.
    proportions: mapping Material_ID -> proportion (either fractions summing to 1 or percents summing to 100).
    basis: one of 'as_received', 'dry', 'ignited'.

    Returns a structured dict containing oxides (percent), moduli and validation info.
    """
    if basis not in SUPPORTED_BASES:
        raise ValueError(f"Unsupported basis '{basis}'. Supported: {sorted(SUPPORTED_BASES)}")

    # Normalize/validate proportions
    if any(v is None for v in proportions.values()):
        raise ValueError("Proportions must be numeric and not None")
    for k, v in proportions.items():
        try:
            fv = float(v)
        except Exception:
            raise ValueError(f"Invalid proportion for material '{k}': {v}")
        if fv < 0:
            raise ValueError(f"Negative proportion for material '{k}': {fv}")

    total = sum(float(v) for v in proportions.values())
    # Accept fractions summing to ~1 or percents summing to ~100
    ok_fraction = math.isclose(total, 1.0, rel_tol=1e-6) or (0.99 <= total <= 1.01)
    ok_percent = 99.0 <= total <= 101.0
    if not (ok_fraction or ok_percent):
        raise ValueError(f"Proportions must sum approximately to 1.0 or 100.0. Got sum={total}")

    # Build materials DataFrame
    df = _ensure_materials_df(materials)

    # Compute weighted oxides (as-received aggregation)
    oxides_raw = _raw_mix.compute_weighted_oxides(df, proportions)

    warnings: List[str] = []

    # Check missing oxide values remain NaN
    missing_oxides = [k for k, v in oxides_raw.items() if v is None or (isinstance(v, float) and math.isnan(v))]
    if missing_oxides:
        warnings.append(f"Missing oxide values for: {missing_oxides}")

    # Mass balance on as-received (percent scale)
    mass_sum = _raw_mix.mass_balance_sum(oxides_raw)
    mass_balance_ok = False
    # If values appear as fractions (sum ~1) treat accordingly
    if mass_sum == 0:
        mass_balance_ok = False
    else:
        target = 100.0 if mass_sum > 1.1 else 1.0
        mass_balance_ok = abs(mass_sum - target) <= tolerance_pct
        if not mass_balance_ok:
            warnings.append(f"Mass balance sum {mass_sum:.3f} differs from expected target {target}")

    result: Dict[str, Any] = {
        "basis": basis,
        "oxides": oxides_raw,
        "mass_balance_sum": mass_sum,
        "mass_balance_ok": mass_balance_ok,
        "warnings": warnings,
    }

    # Basis conversions
    if basis == "ignited":
        # Need LOI to convert; rely on raw_mix.ignited_basis which raises if LOI missing
        try:
            ox_ign, multiplier = _raw_mix.ignited_basis(oxides_raw)
            result["oxides_ignited"] = ox_ign
            result["ignited_multiplier"] = multiplier
            ox_for_moduli = ox_ign
        except Exception as e:
            # propagate but include trace
            raise ValueError(f"Ignited-basis conversion failed: {e}")
    elif basis == "dry":
        # Attempt dry-basis correction if moisture present; otherwise return as-received with warning
        # We check aggregated 'moisture' if present
        moisture = oxides_raw.get("moisture") if isinstance(oxides_raw, dict) else None
        if moisture is None or (isinstance(moisture, float) and math.isnan(moisture)):
            warnings.append("Requested 'dry' basis but no moisture found; returning as_received values")
            ox_for_moduli = oxides_raw
        else:
            try:
                m = float(moisture)
                if m >= 100.0:
                    raise ValueError("Invalid aggregated moisture >= 100%")
                mult = 1.0 / (1.0 - m / 100.0)
                ox_dry = {}
                for k, v in oxides_raw.items():
                    if k == "moisture":
                        ox_dry[k] = 0.0
                    else:
                        ox_dry[k] = float(v) * mult if not (v is None or (isinstance(v, float) and math.isnan(v))) else float("nan")
                result["oxides_dry"] = ox_dry
                ox_for_moduli = ox_dry
            except Exception:
                warnings.append("Failed to compute dry-basis conversion; returning as_received values")
                ox_for_moduli = oxides_raw
    else:
        ox_for_moduli = oxides_raw

    # Compute moduli where possible using ignited-basis convention expected by compute_moduli
    try:
        mods = _raw_mix.compute_moduli(ox_for_moduli)
    except Exception:
        mods = {"LSF": float("nan"), "SM": float("nan"), "AM": float("nan")}

    result.update({"LSF": mods.get("LSF"), "SM": mods.get("SM"), "AM": mods.get("AM")})

    return result


def calculate_lsf(cao: float, sio2: float, al2o3: float, fe2o3: float, basis: str = "ignited") -> float:
    """Calculate LSF using underlying `clinker_chemistry.calculate_lsf`.

    Inputs are assumed to be on the specified `basis`. This wrapper will NOT
    silently convert bases — if your values are not ignited-basis, convert
    them first (e.g. via `calculate_raw_mix_chemistry`).
    """
    if basis not in SUPPORTED_BASES:
        raise ValueError(f"Unsupported basis '{basis}'. Supported: {sorted(SUPPORTED_BASES)}")
    if basis != "ignited":
        raise ValueError("calculate_lsf requires ignited-basis oxide values. Convert basis via calculate_raw_mix_chemistry.")
    return _clinker.calculate_lsf(float(cao), float(sio2), float(al2o3), float(fe2o3))


def calculate_sm(sio2: float, al2o3: float, fe2o3: float, basis: str = "ignited") -> float:
    if basis not in SUPPORTED_BASES:
        raise ValueError(f"Unsupported basis '{basis}'. Supported: {sorted(SUPPORTED_BASES)}")
    if basis != "ignited":
        raise ValueError("calculate_sm requires ignited-basis oxide values. Convert basis via calculate_raw_mix_chemistry.")
    return _clinker.calculate_sm(float(sio2), float(al2o3), float(fe2o3))


def calculate_am(al2o3: float, fe2o3: float, basis: str = "ignited") -> float:
    if basis not in SUPPORTED_BASES:
        raise ValueError(f"Unsupported basis '{basis}'. Supported: {sorted(SUPPORTED_BASES)}")
    if basis != "ignited":
        raise ValueError("calculate_am requires ignited-basis oxide values. Convert basis via calculate_raw_mix_chemistry.")
    return _clinker.calculate_am(float(al2o3), float(fe2o3))
