"""Calculations for clinker chemistry, moduli ratios, and Bogue mineralogical phases."""

from __future__ import annotations

from typing import Dict

def calculate_lsf(cao: float, sio2: float, al2o3: float, fe2o3: float) -> float:
    """Lime saturation factor (LSF) based on Bogue formula."""
    denominator = 2.8 * sio2 + 1.18 * al2o3 + 0.65 * fe2o3
    if denominator == 0:
        raise ValueError("Denominator cannot be zero for LSF calculation.")
    return cao / denominator

def calculate_sm(sio2: float, al2o3: float, fe2o3: float) -> float:
    """Silica modulus (SM)."""
    denominator = al2o3 + fe2o3
    if denominator == 0:
        raise ValueError("Silica modulus denominator cannot be zero.")
    return sio2 / denominator

def calculate_am(al2o3: float, fe2o3: float) -> float:
    """Alumina modulus (AM)."""
    if fe2o3 == 0:
        raise ValueError("Alumina modulus denominator cannot be zero.")
    return al2o3 / fe2o3

def calculate_clinker_ratios(oxide_data: Dict[str, float]) -> Dict[str, float]:
    """Compute key clinker chemistry parameters from oxide percentages."""
    cao = float(oxide_data.get("CaO", 0.0))
    sio2 = float(oxide_data.get("SiO2", 0.0))
    al2o3 = float(oxide_data.get("Al2O3", 0.0))
    fe2o3 = float(oxide_data.get("Fe2O3", 0.0))

    return {
        "LSF": calculate_lsf(cao, sio2, al2o3, fe2o3),
        "SM": calculate_sm(sio2, al2o3, fe2o3),
        "AM": calculate_am(al2o3, fe2o3),
    }

def calculate_bogue_phases(oxide_data: Dict[str, float]) -> Dict[str, float]:
    """Compute standard Bogue mineralogical phase percentages (C3S, C2S, C3A, C4AF)."""
    cao = float(oxide_data.get("CaO", 65.0))
    sio2 = float(oxide_data.get("SiO2", 21.5))
    al2o3 = float(oxide_data.get("Al2O3", 5.2))
    fe2o3 = float(oxide_data.get("Fe2O3", 3.2))
    so3 = float(oxide_data.get("SO3", 0.6))
    free_cao = float(oxide_data.get("Free_CaO", 1.0))

    eff_cao = cao - free_cao

    c3s = max(0.0, 4.071 * eff_cao - 7.600 * sio2 - 6.718 * al2o3 - 1.430 * fe2o3 - 2.852 * so3)
    c2s = max(0.0, 2.867 * sio2 - 0.7544 * c3s)
    c3a = max(0.0, 2.650 * al2o3 - 1.692 * fe2o3)
    c4af = max(0.0, 3.043 * fe2o3)

    return {
        "C3S": round(c3s, 2),
        "C2S": round(c2s, 2),
        "C3A": round(c3a, 2),
        "C4AF": round(c4af, 2),
    }
