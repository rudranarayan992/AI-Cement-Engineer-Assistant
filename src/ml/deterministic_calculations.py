"""Deterministic engineering calculations wrapper.

Provides safe, deterministic APIs for raw-mix chemistry, LSF/SM/AM, mass-balance,
Bogue reference estimates. All outputs are labeled as CALCULATED.
"""
from __future__ import annotations

from typing import Dict, Iterable

from src.chemistry.raw_mix import _to_fraction_dict, OXIDE_COLUMNS
from src.chemistry.chemistry_engine import calculate_raw_mix_chemistry, calculate_lsf, calculate_sm, calculate_am
from src.chemistry.clinker_chemistry import bogue_phase_estimate


def compute_raw_mix_chemistry(raw_materials: Dict[str, Dict[str, float]], proportions: Dict[str, float], basis: str = "as_received") -> Dict[str, float]:
    """Compute deterministic raw-mix oxide composition and moduli.

    Args:
        raw_materials: mapping material_name -> oxide composition dict
        proportions: mapping material_name -> mass proportion (fractions or percents)
        basis: 'as_received' or 'ignited'

    Returns:
        dict with keys: oxides..., 'LSF', 'SM', 'AM', provenance='CALCULATED'
    """
    frac = _to_fraction_dict(proportions)
    # Use chemistry engine to compute weighted composition
    mix = calculate_raw_mix_chemistry(raw_materials, frac, basis=basis)

    lsf = calculate_lsf(mix.get("CaO", 0.0), mix.get("SiO2", 0.0), mix.get("Al2O3", 0.0), mix.get("Fe2O3", 0.0), basis=basis)
    sm = calculate_sm(mix.get("SiO2", 0.0), mix.get("Al2O3", 0.0), mix.get("Fe2O3", 0.0), basis=basis)
    am = calculate_am(mix.get("Al2O3", 0.0), mix.get("Fe2O3", 0.0), basis=basis)

    phases = {}
    try:
        phases = bogue_phase_estimate(mix)
    except Exception:
        phases = {}

    result = {k: float(mix.get(k, 0.0)) for k in OXIDE_COLUMNS}
    result.update({"LSF": float(lsf), "SM": float(sm), "AM": float(am)})
    result.update({"provenance": "CALCULATED", "bogue_reference": phases})
    return result
