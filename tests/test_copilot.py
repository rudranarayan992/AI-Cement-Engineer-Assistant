"""Unit tests for Engineering Copilot."""

from __future__ import annotations

import pytest
from src.llm.engineering_copilot import EngineeringCopilot

def test_copilot_free_cao():
    copilot = EngineeringCopilot()
    ans = copilot.answer_question("Why is Free CaO high?", {"prediction": {"prediction": 2.1, "lsf": 1.01}})
    assert "Root-Cause Analysis" in ans
    assert "Lime Saturation Factor" in ans

def test_copilot_strength():
    copilot = EngineeringCopilot()
    ans = copilot.answer_question("How to improve 28 day strength?")
    assert "Compressive Strength Advisory" in ans
    assert "ASTM C150" in ans

def test_copilot_compare():
    copilot = EngineeringCopilot()
    cand_a = {"cost_per_ton": 12.5, "co2_per_ton": 800.0, "predicted_lsf": 0.96}
    cand_b = {"cost_per_ton": 14.0, "co2_per_ton": 780.0, "predicted_lsf": 0.95}
    comp = copilot.compare_candidates(cand_a, cand_b)
    assert "Candidate A" in comp
    assert "Candidate B" in comp
