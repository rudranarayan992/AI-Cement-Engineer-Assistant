"""Simple cost/value analysis for material substitutions."""
from __future__ import annotations

from typing import Dict, Any


def cost_substitution_analysis(base_recipe: Dict[str, float], prices: Dict[str, float], adjustments: Dict[str, float]) -> Dict[str, Any]:
    """Estimate cost impact of adjustments.

    base_recipe: material -> mass (kg)
    prices: material -> price per kg
    adjustments: material -> delta mass (kg)
    """
    base_cost = sum(base_recipe.get(m, 0.0) * prices.get(m, 0.0) for m in base_recipe)
    new_recipe = {m: base_recipe.get(m, 0.0) + adjustments.get(m, 0.0) for m in base_recipe}
    new_cost = sum(new_recipe.get(m, 0.0) * prices.get(m, 0.0) for m in new_recipe)
    delta = new_cost - base_cost
    return {"base_cost": base_cost, "new_cost": new_cost, "delta": delta, "new_recipe": new_recipe}
