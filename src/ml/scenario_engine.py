"""Thin wrapper integrating existing raw_mix scenarios and optimization modules.

Exposes a simple API for generating scenarios and comparing them.
"""
from __future__ import annotations

from typing import Dict, Any, List

from src.optimization.raw_mix_scenarios import calculate_raw_mix_scenario, compare_scenarios, deterministic_sensitivity_analysis


def run_scenario(base_recipe: Dict[str, float], adjustments: Dict[str, float]) -> Dict[str, Any]:
    """Run a single scenario adjustment and return computed chemistry and checks."""
    scenario = calculate_raw_mix_scenario(base_recipe, adjustments)
    return scenario


def compare(list_of_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
    return compare_scenarios(list_of_scenarios)


def sensitivity(recipe: Dict[str, float], param: str, delta: float = 0.01) -> Dict[str, Any]:
    return deterministic_sensitivity_analysis(recipe, param, delta)
