"""Unit tests for raw mix optimization solver."""

from __future__ import annotations

import pytest
from src.optimization.raw_mix_optimizer import optimize_raw_mix, generate_candidate_blends

def test_optimize_raw_mix():
    res = optimize_raw_mix(target_lsf=0.96, target_sm=2.30, target_am=1.80)
    assert "proportions_pct" in res
    props = res["proportions_pct"]
    assert sum(props.values()) == pytest.approx(100.0, abs=0.1)
    assert 0.90 <= res["achieved_moduli"]["LSF"] <= 1.02
    assert res["total_cost_usd_per_ton"] > 0
    assert res["total_co2_kg_per_ton"] > 0

def test_generate_candidate_blends():
    cands = generate_candidate_blends({"LSF": 0.96, "SM": 2.30, "AM": 1.80})
    assert len(cands) >= 3
    assert cands[0]["cost_per_ton"] > 0
