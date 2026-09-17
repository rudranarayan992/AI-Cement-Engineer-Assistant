"""Unit tests for physics_constraints module.

Test coverage:
1. Valid raw mix
2. Negative proportion
3. Incorrect total
4. LSF below/above range
5. SM below/above range
6. AM below/above range
7. Invalid chemistry
8. Invalid phase prediction
9. Free CaO violation
10. Aggregate valid case
11. Aggregate invalid case
12. Warnings vs hard violations
13. Missing values handling
14. Custom material limits
15. Custom moduli ranges
"""
import importlib.util
import math
import os

import pytest

# Load module by path to avoid package-level imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
SRC_ROOT = os.path.join(ROOT, "src", "validation")


def _load(name: str):
    # Try multiple path strategies to find the module
    paths_to_try = [
        os.path.join(SRC_ROOT, f"{name}.py"),  # Primary: repo-root/src/validation
        os.path.abspath(os.path.join(ROOT, "src", "validation", f"{name}.py")),  # explicit repo-root lookup
        os.path.abspath(os.path.join(os.getcwd(), "src", "validation", f"{name}.py")),  # current working directory lookup
        os.path.abspath(os.path.join(os.getcwd(), "AI_Cement_Project", "src", "validation", f"{name}.py")),  # nested-project fallback
    ]
    
    path = None
    for candidate in paths_to_try:
        if os.path.exists(candidate):
            path = candidate
            break
    
    if not path:
        raise FileNotFoundError(f"Module {name} not found. Tried: {paths_to_try}")
    
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    # Register in sys.modules before executing to support dataclasses
    import sys
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


pc = _load("physics_constraints")


class TestRawMixValidation:
    """Test raw-material proportion validation."""

    def test_valid_raw_mix_proportions(self):
        """Test valid raw mix (proportions sum to 100%)."""
        props = {"limestone": 78.0, "clay": 14.0, "iron_ore": 3.0, "silica": 5.0}
        result = pc.validate_raw_mix_proportions(props)

        assert result["valid"] is True
        assert len(result["violations"]) == 0
        assert result["total"] == 100.0

    def test_negative_proportion_violation(self):
        """Test detection of negative raw-material proportion."""
        props = {"limestone": 80.0, "clay": -10.0, "iron_ore": 30.0}
        result = pc.validate_raw_mix_proportions(props)

        assert result["valid"] is False
        assert any("clay" in v and ("-" in v or "minimum" in v.lower()) for v in result["violations"])

    def test_proportion_exceeds_max(self):
        """Test detection of single material proportion > 100%."""
        props = {"limestone": 110.0, "clay": 10.0}
        result = pc.validate_raw_mix_proportions(props)

        assert result["valid"] is False
        assert any("limestone" in v and "maximum" in v.lower() for v in result["violations"])

    def test_incorrect_total_sum(self):
        """Test detection of raw mix total != 100%."""
        props = {"limestone": 70.0, "clay": 15.0}  # Sum = 85%
        result = pc.validate_raw_mix_proportions(props)

        assert result["valid"] is False
        assert any("outside tolerance" in v.lower() for v in result["violations"])

    def test_custom_material_limits(self):
        """Test custom per-material min/max limits."""
        props = {"limestone": 80.0, "clay": 12.0, "iron_ore": 8.0}
        limits = pc.ConstraintLimits()
        limits.material_limits = {"limestone": (70.0, 85.0), "iron_ore": (0.0, 5.0)}

        result = pc.validate_raw_mix_proportions(props, limits)

        assert result["valid"] is False
        assert any("iron_ore" in v for v in result["violations"])


class TestChemistryValidation:
    """Test oxide composition validation."""

    def test_valid_chemistry(self):
        """Test valid oxide composition."""
        oxides = {"CaO": 65.0, "SiO2": 22.0, "Al2O3": 5.0, "Fe2O3": 3.0}
        result = pc.validate_chemistry_values(oxides)

        assert result["valid"] is True
        assert len(result["violations"]) == 0

    def test_negative_oxide_violation(self):
        """Test detection of negative oxide value."""
        oxides = {"CaO": 65.0, "SiO2": -5.0, "Al2O3": 5.0, "Fe2O3": 3.0}
        result = pc.validate_chemistry_values(oxides)

        assert result["valid"] is False
        assert any("SiO2" in v and "negative" in v.lower() for v in result["violations"])

    def test_nan_oxide_violation(self):
        """Test detection of NaN oxide value."""
        oxides = {"CaO": 65.0, "SiO2": float("nan"), "Al2O3": 5.0, "Fe2O3": 3.0}
        result = pc.validate_chemistry_values(oxides)

        assert result["valid"] is False
        assert any("SiO2" in v and "nan" in v.lower() for v in result["violations"])

    def test_infinite_oxide_violation(self):
        """Test detection of infinite oxide value."""
        oxides = {"CaO": 65.0, "SiO2": float("inf"), "Al2O3": 5.0, "Fe2O3": 3.0}
        result = pc.validate_chemistry_values(oxides)

        assert result["valid"] is False
        assert any("infinite" in v.lower() for v in result["violations"])

    def test_missing_oxide_warning(self):
        """Test warning for missing oxide (None)."""
        oxides = {"CaO": 65.0, "SiO2": None, "Al2O3": 5.0, "Fe2O3": 3.0}
        result = pc.validate_chemistry_values(oxides)

        assert len(result["warnings"]) > 0


class TestModuliValidation:
    """Test LSF, SM, AM validation."""

    def test_valid_moduli(self):
        """Test valid moduli within configured ranges."""
        # CaO=65, SiO2=22, Al2O3=5, Fe2O3=3
        # LSF = 65 / (2.8*22 + 1.18*5 + 0.65*3) ≈ 65 / 67.05 ≈ 0.97
        # SM = 22 / (5 + 3) ≈ 2.75
        # AM = 5 / 3 ≈ 1.67
        result = pc.validate_moduli(65.0, 22.0, 5.0, 3.0)

        assert result["valid"] is True
        assert 0.90 <= result["LSF"] <= 1.05  # Default limits
        assert 2.00 <= result["SM"] <= 3.00
        assert 1.40 <= result["AM"] <= 2.20

    def test_lsf_below_range(self):
        """Test LSF below configured minimum."""
        # Create oxides that produce low LSF
        # Low CaO or high (SiO2 + Al2O3 + Fe2O3) → low LSF
        result = pc.validate_moduli(50.0, 25.0, 10.0, 5.0)

        assert result["valid"] is False
        assert any("LSF" in v and "minimum" in v.lower() for v in result["violations"])

    def test_lsf_above_range(self):
        """Test LSF above configured maximum."""
        # High CaO or low (SiO2 + Al2O3 + Fe2O3) → high LSF
        result = pc.validate_moduli(75.0, 10.0, 2.0, 1.0)

        assert result["valid"] is False
        assert any("LSF" in v and "maximum" in v.lower() for v in result["violations"])

    def test_sm_below_range(self):
        """Test SM below configured minimum."""
        # Low SiO2 or high (Al2O3 + Fe2O3) → low SM
        result = pc.validate_moduli(65.0, 12.0, 15.0, 10.0)

        assert result["valid"] is False
        assert any("SM" in v and "minimum" in v.lower() for v in result["violations"])

    def test_sm_above_range(self):
        """Test SM above configured maximum."""
        # High SiO2 or low (Al2O3 + Fe2O3) → high SM
        result = pc.validate_moduli(65.0, 35.0, 2.0, 1.0)

        assert result["valid"] is False
        assert any("SM" in v and "maximum" in v.lower() for v in result["violations"])

    def test_am_below_range(self):
        """Test AM below configured minimum."""
        # Low Al2O3 or high Fe2O3 → low AM
        result = pc.validate_moduli(65.0, 22.0, 2.0, 5.0)

        assert result["valid"] is False
        assert any("AM" in v and "minimum" in v.lower() for v in result["violations"])

    def test_am_above_range(self):
        """Test AM above configured maximum."""
        # High Al2O3 or low Fe2O3 → high AM
        result = pc.validate_moduli(65.0, 22.0, 10.0, 1.0)

        assert result["valid"] is False
        assert any("AM" in v and "maximum" in v.lower() for v in result["violations"])

    def test_custom_moduli_limits(self):
        """Test custom LSF/SM/AM limits."""
        limits = pc.ConstraintLimits(lsf_min=0.95, lsf_max=1.00, sm_min=2.40, sm_max=2.60)
        # Standard values: LSF≈0.97, SM≈2.75
        result = pc.validate_moduli(65.0, 22.0, 5.0, 3.0, limits)

        # LSF should be OK, but SM should fail (> 2.60)
        assert any("SM" in v and "maximum" in v.lower() for v in result["violations"])


class TestPhaseValidation:
    """Test clinker phase prediction validation."""

    def test_valid_phase_prediction(self):
        """Test valid clinker phases."""
        phases = {"C3S": 65.0, "C2S": 15.0, "C3A": 8.0, "C4AF": 12.0}
        result = pc.validate_phase_prediction(phases)

        assert result["valid"] is True

    def test_negative_phase_violation(self):
        """Test detection of negative phase."""
        phases = {"C3S": 70.0, "C2S": -5.0, "C3A": 10.0, "C4AF": 25.0}
        result = pc.validate_phase_prediction(phases)

        assert result["valid"] is False
        assert any("C2S" in v for v in result["violations"])

    def test_phase_exceeds_max(self):
        """Test detection of phase > 100%."""
        phases = {"C3S": 120.0, "C2S": 0.0, "C3A": 0.0, "C4AF": 0.0}
        result = pc.validate_phase_prediction(phases)

        assert result["valid"] is False
        assert any("C3S" in v for v in result["violations"])

    def test_free_cao_negative_violation(self):
        """Test detection of negative Free CaO."""
        phases = {"C3S": 65.0, "C2S": 15.0, "C3A": 8.0, "C4AF": 9.0, "Free_CaO": -1.0}
        result = pc.validate_phase_prediction(phases)

        assert result["valid"] is False
        assert any("Free CaO" in v and "negative" in v.lower() for v in result["violations"])

    def test_free_cao_exceeds_max(self):
        """Test detection of Free CaO > limit."""
        limits = pc.ConstraintLimits(free_cao_max=2.0)
        phases = {"C3S": 65.0, "C2S": 15.0, "C3A": 8.0, "C4AF": 9.0, "Free_CaO": 3.0}
        result = pc.validate_phase_prediction(phases, limits)

        assert result["valid"] is False
        assert any("Free CaO" in v and "maximum" in v.lower() for v in result["violations"])


class TestAggregateValidation:
    """Test comprehensive multi-layer validation."""

    def test_aggregate_valid_case(self):
        """Test aggregate validation with all valid inputs."""
        raw_mix = {"limestone": 78.0, "clay": 14.0, "iron_ore": 3.0, "silica": 5.0}
        oxides = {"CaO": 65.0, "SiO2": 22.0, "Al2O3": 5.0, "Fe2O3": 3.0}
        phases = {"C3S": 65.0, "C2S": 15.0, "C3A": 8.0, "C4AF": 12.0}

        result = pc.validate_all(raw_mix, oxides, phases)

        assert result["valid"] is True
        assert len(result["violations"]) == 0
        assert result["constraint_score"] == 0.0

    def test_aggregate_invalid_raw_mix(self):
        """Test aggregate validation with invalid raw mix."""
        raw_mix = {"limestone": 70.0, "clay": 15.0}  # Sum = 85%
        oxides = {"CaO": 65.0, "SiO2": 22.0, "Al2O3": 5.0, "Fe2O3": 3.0}
        phases = {"C3S": 65.0, "C2S": 15.0, "C3A": 8.0, "C4AF": 12.0}

        result = pc.validate_all(raw_mix, oxides, phases)

        assert result["valid"] is False
        assert result["constraint_score"] > 0.0

    def test_aggregate_invalid_chemistry(self):
        """Test aggregate validation with invalid chemistry."""
        raw_mix = {"limestone": 78.0, "clay": 14.0, "iron_ore": 3.0, "silica": 5.0}
        oxides = {"CaO": 65.0, "SiO2": -5.0, "Al2O3": 5.0, "Fe2O3": 3.0}
        phases = {"C3S": 65.0, "C2S": 15.0, "C3A": 8.0, "C4AF": 12.0}

        result = pc.validate_all(raw_mix, oxides, phases)

        assert result["valid"] is False
        assert "chemistry" in result["checks"]
        assert not result["checks"]["chemistry"]["valid"]

    def test_aggregate_invalid_moduli(self):
        """Test aggregate validation with out-of-range moduli."""
        raw_mix = {"limestone": 78.0, "clay": 14.0, "iron_ore": 3.0, "silica": 5.0}
        oxides = {"CaO": 50.0, "SiO2": 30.0, "Al2O3": 10.0, "Fe2O3": 5.0}  # Very low LSF
        phases = {"C3S": 65.0, "C2S": 15.0, "C3A": 8.0, "C4AF": 12.0}

        result = pc.validate_all(raw_mix, oxides, phases)

        assert result["valid"] is False
        assert "moduli" in result["checks"]
        assert not result["checks"]["moduli"]["valid"]

    def test_aggregate_invalid_phases(self):
        """Test aggregate validation with invalid phases."""
        raw_mix = {"limestone": 78.0, "clay": 14.0, "iron_ore": 3.0, "silica": 5.0}
        oxides = {"CaO": 65.0, "SiO2": 22.0, "Al2O3": 5.0, "Fe2O3": 3.0}
        phases = {"C3S": 120.0, "C2S": -10.0, "C3A": 0.0, "C4AF": 0.0}

        result = pc.validate_all(raw_mix, oxides, phases)

        assert result["valid"] is False
        assert "phases" in result["checks"]
        assert not result["checks"]["phases"]["valid"]

    def test_aggregate_multiple_violations(self):
        """Test aggregate validation with multiple violations."""
        raw_mix = {"limestone": 70.0, "clay": 15.0}  # Invalid sum
        oxides = {"CaO": 65.0, "SiO2": -5.0, "Al2O3": 5.0, "Fe2O3": 3.0}  # Negative SiO2
        phases = {"C3S": 120.0, "C2S": 0.0, "C3A": 0.0, "C4AF": 0.0}  # Invalid phase

        result = pc.validate_all(raw_mix, oxides, phases)

        assert result["valid"] is False
        assert len(result["violations"]) >= 3

    def test_aggregate_constraint_score_scales(self):
        """Test that constraint_score increases with violations."""
        valid_inputs = {
            "raw_mix_proportions": {"limestone": 78.0, "clay": 14.0, "iron_ore": 3.0, "silica": 5.0},
            "input_oxides": {"CaO": 65.0, "SiO2": 22.0, "Al2O3": 5.0, "Fe2O3": 3.0},
            "predicted_phases": {"C3S": 65.0, "C2S": 15.0, "C3A": 8.0, "C4AF": 12.0},
        }

        invalid_inputs = {
            "raw_mix_proportions": {"limestone": 70.0},  # Invalid sum
            "input_oxides": {"CaO": 50.0, "SiO2": 30.0, "Al2O3": 10.0, "Fe2O3": 5.0},
            "predicted_phases": {"C3S": 120.0, "C2S": -10.0, "C3A": 0.0, "C4AF": 0.0},
        }

        valid_result = pc.validate_all(**valid_inputs)
        invalid_result = pc.validate_all(**invalid_inputs)

        assert valid_result["constraint_score"] < invalid_result["constraint_score"]


class TestPartialInputs:
    """Test validation with partial inputs (some None)."""

    def test_raw_mix_only(self):
        """Test validation with only raw mix proportions."""
        raw_mix = {"limestone": 78.0, "clay": 14.0, "iron_ore": 3.0, "silica": 5.0}
        result = pc.validate_all(raw_mix_proportions=raw_mix)

        assert "raw_mix" in result["checks"]
        assert "chemistry" not in result["checks"]
        assert "moduli" not in result["checks"]

    def test_chemistry_only(self):
        """Test validation with only oxide composition."""
        oxides = {"CaO": 65.0, "SiO2": 22.0, "Al2O3": 5.0, "Fe2O3": 3.0}
        result = pc.validate_all(input_oxides=oxides)

        assert "chemistry" in result["checks"]
        assert "moduli" in result["checks"]
        assert "raw_mix" not in result["checks"]

    def test_phases_only(self):
        """Test validation with only phase predictions."""
        phases = {"C3S": 65.0, "C2S": 15.0, "C3A": 8.0, "C4AF": 12.0}
        result = pc.validate_all(predicted_phases=phases)

        assert "phases" in result["checks"]
        assert "raw_mix" not in result["checks"]
        assert "chemistry" not in result["checks"]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_moduli_denominator(self):
        """Test handling of zero denominator in moduli calculations."""
        # Al2O3 = Fe2O3 = 0 → SM and AM would have zero denominators
        result = pc.validate_moduli(65.0, 22.0, 0.0, 0.0)

        assert not result["valid"]
        assert any("SM" in v or "AM" in v for v in result["violations"])

    def test_empty_proportions(self):
        """Test handling of empty raw mix dict."""
        props = {}
        result = pc.validate_raw_mix_proportions(props)

        assert result["valid"] is False  # Sum = 0, not 100

    def test_nan_tolerance(self):
        """Test tolerance handling with tolerance_pct edge case."""
        limits = pc.ConstraintLimits(raw_mix_tolerance=0.1)  # Very tight tolerance
        props = {"limestone": 98.05, "clay": 1.95}  # Sum = 100.0, but within tolerance
        result = pc.validate_raw_mix_proportions(props, limits)

        assert result["valid"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
