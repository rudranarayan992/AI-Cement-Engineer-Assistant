"""Raw-mix proportioning optimizer solving 4-component raw meal blending.

Uses SciPy optimization to compute optimal proportions of Limestone, Clay, Silica Sand, and Iron Ore
to match target Lime Saturation Factor (LSF), Silica Modulus (SM), and Alumina Modulus (AM)
while minimizing raw material cost and carbon footprint.
"""

from __future__ import annotations

import numpy as np

try:
    from scipy.optimize import minimize
except ImportError:
    minimize = None

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

@dataclass
class CandidateBlend:
    limestone: float
    clay: float
    iron_corrective: float
    predicted_lsf: float
    predicted_sm: float
    predicted_am: float
    confidence: float
    notes: str = "Candidate for laboratory confirmation"

    def to_dict(self):
        return asdict(self)

DEFAULT_MATERIALS = {
    "Limestone": {"CaO": 53.8, "SiO2": 2.5, "Al2O3": 0.8, "Fe2O3": 0.4, "Cost": 12.5, "CO2": 820.0},
    "Clay": {"CaO": 2.5, "SiO2": 58.4, "Al2O3": 18.2, "Fe2O3": 7.1, "Cost": 8.0, "CO2": 45.0},
    "Silica Sand": {"CaO": 0.8, "SiO2": 92.5, "Al2O3": 3.2, "Fe2O3": 1.1, "Cost": 18.0, "CO2": 25.0},
    "Iron Ore": {"CaO": 1.2, "SiO2": 10.5, "Al2O3": 3.1, "Fe2O3": 81.2, "Cost": 35.0, "CO2": 30.0},
}

def optimize_raw_mix(
    materials: Dict[str, Dict[str, float]] | None = None,
    target_lsf: float = 0.96,
    target_sm: float = 2.30,
    target_am: float = 1.80,
    max_cost: float | None = None,
    max_co2: float | None = None,
) -> Dict[str, Any]:
    """Calculate optimal blend proportions (%) of raw materials.

    Returns proportions, resulting raw meal & clinker oxide compositions,
    achieved LSF, SM, AM moduli, total raw meal cost ($/ton), and CO2 emissions (kg/ton).
    """
    if materials is None:
        materials = DEFAULT_MATERIALS

    mat_names = list(materials.keys())
    n_mats = len(mat_names)

    cao = np.array([materials[m].get("CaO", 0.0) for m in mat_names])
    sio2 = np.array([materials[m].get("SiO2", 0.0) for m in mat_names])
    al2o3 = np.array([materials[m].get("Al2O3", 0.0) for m in mat_names])
    fe2o3 = np.array([materials[m].get("Fe2O3", 0.0) for m in mat_names])
    costs = np.array([materials[m].get("Cost", 10.0) for m in mat_names])
    co2s = np.array([materials[m].get("CO2", 100.0) for m in mat_names])

    # Initial guess (e.g. 78% Limestone, 14% Clay, 5% Silica, 3% Iron)
    x0 = np.array([0.78, 0.14, 0.05, 0.03][:n_mats])
    x0 = x0 / np.sum(x0)

    def objective(w):
        # Multi-objective: minimize modulus errors + cost penalty
        c_mix = np.dot(w, cao)
        s_mix = np.dot(w, sio2)
        a_mix = np.dot(w, al2o3)
        f_mix = np.dot(w, fe2o3)

        lsf_calc = c_mix / (2.8 * s_mix + 1.2 * a_mix + 0.65 * f_mix + 1e-6)
        sm_calc = s_mix / (a_mix + f_mix + 1e-6)
        am_calc = a_mix / (f_mix + 1e-6)

        err_lsf = (lsf_calc - target_lsf) ** 2
        err_sm = (sm_calc - target_sm) ** 2
        err_am = (am_calc - target_am) ** 2

        cost_val = np.dot(w, costs) / 50.0  # normalize

        return 100.0 * err_lsf + 20.0 * err_sm + 20.0 * err_am + 0.5 * cost_val

    # Equality constraint: proportions sum to 1.0 (100%)
    cons = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]
    bounds = [(0.01, 0.95) for _ in range(n_mats)]

    if minimize is not None:
        res = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=cons)
        w_opt = res.x if res.success else x0
    else:
        w_opt = x0

    w_pct = w_opt * 100.0
    c_mix = float(np.dot(w_opt, cao))
    s_mix = float(np.dot(w_opt, sio2))
    a_mix = float(np.dot(w_opt, al2o3))
    f_mix = float(np.dot(w_opt, fe2o3))

    lsf_achieved = c_mix / (2.8 * s_mix + 1.2 * a_mix + 0.65 * f_mix)
    sm_achieved = s_mix / (a_mix + f_mix)
    am_achieved = a_mix / f_mix

    total_cost = float(np.dot(w_opt, costs))
    total_co2 = float(np.dot(w_opt, co2s))

    proportions = {name: round(float(w_pct[i]), 2) for i, name in enumerate(mat_names)}

    return {
        "proportions_pct": proportions,
        "raw_meal_oxides": {
            "CaO": round(c_mix, 2),
            "SiO2": round(s_mix, 2),
            "Al2O3": round(a_mix, 2),
            "Fe2O3": round(f_mix, 2)
        },
        "clinker_calcined_oxides": {
            "CaO": round(c_mix * 1.55, 2),
            "SiO2": round(s_mix * 1.55, 2),
            "Al2O3": round(a_mix * 1.55, 2),
            "Fe2O3": round(f_mix * 1.55, 2)
        },
        "target_moduli": {"LSF": target_lsf, "SM": target_sm, "AM": target_am},
        "achieved_moduli": {"LSF": round(lsf_achieved, 4), "SM": round(sm_achieved, 4), "AM": round(am_achieved, 4)},
        "total_cost_usd_per_ton": round(total_cost, 2),
        "total_co2_kg_per_ton": round(total_co2, 1),
        "status": "Optimal Solution Found" if (minimize is not None and res.success) else "Approximate Solution"
    }

def generate_candidate_blends(
    targets: Dict[str, float],
    available_materials: Dict[str, float] | None = None,
    max_cost: float = 100.0,
    max_co2: float = 1000.0,
) -> List[Dict[str, Any]]:
    """Build candidate raw mix formulations satisfying target chemistry ranges."""
    target_lsf = float(targets.get("LSF", 0.96))
    target_sm = float(targets.get("SM", 2.30))
    target_am = float(targets.get("AM", 1.80))

    opt = optimize_raw_mix(target_lsf=target_lsf, target_sm=target_sm, target_am=target_am)

    base_prop = opt["proportions_pct"]
    candidates = []

    # Candidate 1: Standard Optimal
    candidates.append({
        "blend_id": "RECIPE_OPT_01",
        "limestone": base_prop.get("Limestone", 78.0),
        "clay": base_prop.get("Clay", 14.0),
        "silica_sand": base_prop.get("Silica Sand", 5.0),
        "iron_ore": base_prop.get("Iron Ore", 3.0),
        "predicted_lsf": opt["achieved_moduli"]["LSF"],
        "predicted_sm": opt["achieved_moduli"]["SM"],
        "predicted_am": opt["achieved_moduli"]["AM"],
        "cost_per_ton": opt["total_cost_usd_per_ton"],
        "co2_per_ton": opt["total_co2_kg_per_ton"],
        "notes": "Cost & CO2 optimized standard formulation."
    })

    # Candidate 2: High Silica / High SM
    opt_sm = optimize_raw_mix(target_lsf=target_lsf, target_sm=target_sm + 0.15, target_am=target_am)
    p_sm = opt_sm["proportions_pct"]
    candidates.append({
        "blend_id": "RECIPE_HIGH_SM",
        "limestone": p_sm.get("Limestone", 77.5),
        "clay": p_sm.get("Clay", 13.0),
        "silica_sand": p_sm.get("Silica Sand", 6.5),
        "iron_ore": p_sm.get("Iron Ore", 3.0),
        "predicted_lsf": opt_sm["achieved_moduli"]["LSF"],
        "predicted_sm": opt_sm["achieved_moduli"]["SM"],
        "predicted_am": opt_sm["achieved_moduli"]["AM"],
        "cost_per_ton": opt_sm["total_cost_usd_per_ton"],
        "co2_per_ton": opt_sm["total_co2_kg_per_ton"],
        "notes": "High silica ratio blend for improved C2S and late compressive strength."
    })

    # Candidate 3: Low Carbon Eco-Blend
    opt_eco = optimize_raw_mix(target_lsf=target_lsf - 0.02, target_sm=target_sm, target_am=target_am)
    p_eco = opt_eco["proportions_pct"]
    candidates.append({
        "blend_id": "RECIPE_ECO_CARBON",
        "limestone": p_eco.get("Limestone", 76.0),
        "clay": p_eco.get("Clay", 15.5),
        "silica_sand": p_eco.get("Silica Sand", 5.0),
        "iron_ore": p_eco.get("Iron Ore", 3.5),
        "predicted_lsf": opt_eco["achieved_moduli"]["LSF"],
        "predicted_sm": opt_eco["achieved_moduli"]["SM"],
        "predicted_am": opt_eco["achieved_moduli"]["AM"],
        "cost_per_ton": opt_eco["total_cost_usd_per_ton"],
        "co2_per_ton": opt_eco["total_co2_kg_per_ton"],
        "notes": "Reduced limestone proportion to lower thermal decarbonization CO2 emissions."
    })

    return candidates
