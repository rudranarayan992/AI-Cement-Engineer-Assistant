"""Unit tests for phase_constraints module.

Tests cover:
1. Valid phase prediction
2. Negative phase prediction
3. NaN prediction
4. Missing oxide
5. Valid phase reconstruction
6. Invalid phase reconstruction
7. Phase-sum violation
8. Oxide residual calculation
9. Physical-bound violation
10. Valid prediction returning no violations
11. Invalid prediction returning explicit violations

All tests use transparent, hand-calculated examples where possible.
"""
import importlib.util
import math
import os

import pytest

# Load module by path to avoid package-level imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
SRC_ROOT = os.path.join(ROOT, "src", "chemistry")


def _load(name: str):
    path = os.path.join(SRC_ROOT, f"{name}.py")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Module not found at {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pc = _load("phase_constraints")


class TestPhaseToOxideReconstruction:
    """Test oxide reconstruction from phase fractions."""

    def test_valid_phase_reconstruction(self):
        """Test reconstruction from simple, valid phases."""
        # All C3S: should reconstruct to pure C3S oxide composition
        phases = {"C3S": 100.0, "C2S": 0.0, "C3A": 0.0, "C4AF": 0.0}
        oxides = pc.phase_to_oxide_reconstruction(phases)

        # C3S: CaO=73.6%, SiO2=26.4%
        assert math.isclose(oxides["CaO"], 73.6, rel_tol=1e-4)
        assert math.isclose(oxides["SiO2"], 26.4, rel_tol=1e-4)
        assert math.isclose(oxides["Al2O3"], 0.0, abs_tol=1e-9)
        assert math.isclose(oxides["Fe2O3"], 0.0, abs_tol=1e-9)

    def test_mixed_phase_reconstruction(self):
        """Test reconstruction from a realistic mix of phases."""
        # Example: 65% C3S, 15% C2S, 8% C3A, 12% C4AF
        phases = {"C3S": 65.0, "C2S": 15.0, "C3A": 8.0, "C4AF": 12.0}
        oxides = pc.phase_to_oxide_reconstruction(phases)

        # Manual calculation:
        # CaO: 65*(73.6/100) + 15*(65.2/100) + 8*(62.4/100) + 12*(46.2/100)
        #    = 47.84 + 9.78 + 4.992 + 5.544 = 68.156
        expected_cao = 65 * 0.736 + 15 * 0.652 + 8 * 0.624 + 12 * 0.462
        assert math.isclose(oxides["CaO"], expected_cao, rel_tol=1e-4)

    def test_invalid_phase_name(self):
        """Test that unknown phase names raise ValueError."""
        phases = {"C3S": 50.0, "UNKNOWN": 50.0}
        with pytest.raises(ValueError, match="Unknown phase"):
            pc.phase_to_oxide_reconstruction(phases)

    def test_invalid_basis(self):
        """Test that invalid basis raises ValueError."""
        phases = {"C3S": 100.0}
        with pytest.raises(ValueError, match="Unsupported phase_basis"):
            pc.phase_to_oxide_reconstruction(phases, phase_basis="invalid")

    def test_nan_phase_raises(self):
        """Test that NaN phase values raise ValueError."""
        phases = {"C3S": float("nan"), "C2S": 50.0}
        with pytest.raises(ValueError, match="invalid value"):
            pc.phase_to_oxide_reconstruction(phases)

    def test_infinite_phase_raises(self):
        """Test that infinite phase values raise ValueError."""
        phases = {"C3S": float("inf"), "C2S": 50.0}
        with pytest.raises(ValueError, match="invalid value"):
            pc.phase_to_oxide_reconstruction(phases)


class TestStoichiometricResidual:
    """Test stoichiometric residual calculation."""

    def test_perfect_match(self):
        """Test residuals when reconstructed oxides perfectly match input."""
        # Pure C3S phases
        phases = {"C3S": 100.0, "C2S": 0.0, "C3A": 0.0, "C4AF": 0.0}
        oxides = {"CaO": 73.6, "SiO2": 26.4, "Al2O3": 0.0, "Fe2O3": 0.0}

        result = pc.calculate_stoichiometric_residual(oxides, phases, normalize_by="none")

        # Residuals should be near zero
        assert math.isclose(result["residuals"]["CaO"], 0.0, abs_tol=0.01)
        assert math.isclose(result["residuals"]["SiO2"], 0.0, abs_tol=0.01)
        assert result["total_residual"] < 0.1

    def test_mismatch_raises_residual(self):
        """Test that oxide/phase mismatch produces non-zero residuals."""
        phases = {"C3S": 100.0, "C2S": 0.0, "C3A": 0.0, "C4AF": 0.0}
        oxides = {"CaO": 65.0, "SiO2": 30.0, "Al2O3": 3.0, "Fe2O3": 2.0}

        result = pc.calculate_stoichiometric_residual(oxides, phases, normalize_by="none")

        # Input CaO (65) - reconstructed C3S CaO (73.6) = -8.6
        # This should produce negative residual for CaO
        assert result["residuals"]["CaO"] < 0.0

    def test_residual_normalization_by_input(self):
        """Test residual normalization by input values."""
        phases = {"C3S": 50.0, "C2S": 0.0, "C3A": 0.0, "C4AF": 0.0}
        oxides = {"CaO": 50.0, "SiO2": 20.0, "Al2O3": 0.0, "Fe2O3": 0.0}

        result = pc.calculate_stoichiometric_residual(oxides, phases, normalize_by="input")

        # Check normalized residuals exist
        assert "residuals_normalized" in result
        assert "CaO" in result["residuals_normalized"]

    def test_missing_oxide_values(self):
        """Test handling of missing oxide values in input."""
        phases = {"C3S": 100.0, "C2S": 0.0, "C3A": 0.0, "C4AF": 0.0}
        oxides = {"CaO": 73.6}  # Missing SiO2, Al2O3, Fe2O3

        result = pc.calculate_stoichiometric_residual(oxides, phases, normalize_by="none")

        # Should treat missing oxides as 0.0
        assert "residuals" in result
        assert "SiO2" in result["residuals"]


class TestPhaseSumResidual:
    """Test phase-sum validation."""

    def test_valid_mass_percent_sum(self):
        """Test phase sum near 100% (mass percent basis)."""
        phases = {"C3S": 65.0, "C2S": 15.0, "C3A": 8.0, "C4AF": 12.0}
        result = pc.calculate_phase_sum_residual(phases)

        assert result["valid"] is True
        assert result["sum_basis"] == "mass_percent"
        assert result["phase_sum"] == 100.0

    def test_valid_fraction_sum(self):
        """Test phase sum near 1.0 (fraction basis)."""
        phases = {"C3S": 0.65, "C2S": 0.15, "C3A": 0.08, "C4AF": 0.12}
        result = pc.calculate_phase_sum_residual(phases)

        assert result["valid"] is True
        assert result["sum_basis"] == "fraction"

    def test_invalid_low_sum(self):
        """Test phase sum too low (incomplete phases)."""
        phases = {"C3S": 30.0, "C2S": 20.0}  # Sum = 50%
        result = pc.calculate_phase_sum_residual(phases)

        assert result["valid"] is False
        assert len(result["warnings"]) > 0

    def test_invalid_high_sum(self):
        """Test phase sum too high (over 110%)."""
        phases = {"C3S": 80.0, "C2S": 40.0}  # Sum = 120%
        result = pc.calculate_phase_sum_residual(phases)

        assert result["valid"] is False
        assert len(result["warnings"]) > 0


class TestPhysicalBoundPenalty:
    """Test physical bound checking."""

    def test_negative_phase_violation(self):
        """Test detection of negative phase fractions."""
        phases = {"C3S": 80.0, "C2S": -10.0, "C3A": 15.0, "C4AF": 15.0}
        result = pc.calculate_physical_bound_penalty(phases)

        assert result["valid"] is False
        assert len(result["violations"]) > 0
        assert result["penalty"] > 0.0

    def test_phase_exceeds_upper_bound(self):
        """Test detection of phases exceeding 100%."""
        phases = {"C3S": 120.0, "C2S": 0.0, "C3A": 0.0, "C4AF": 0.0}
        result = pc.calculate_physical_bound_penalty(phases)

        assert result["valid"] is False
        assert any("upper bound" in v.lower() for v in result["violations"])

    def test_nan_phase_violation(self):
        """Test detection of NaN phases."""
        phases = {"C3S": float("nan"), "C2S": 50.0, "C3A": 25.0, "C4AF": 25.0}
        result = pc.calculate_physical_bound_penalty(phases)

        assert result["valid"] is False
        assert any("nan" in v.lower() for v in result["violations"])

    def test_infinite_phase_violation(self):
        """Test detection of infinite phases."""
        phases = {"C3S": float("inf"), "C2S": 50.0, "C3A": 0.0, "C4AF": 0.0}
        result = pc.calculate_physical_bound_penalty(phases)

        assert result["valid"] is False
        assert any("infinite" in v.lower() for v in result["violations"])

    def test_custom_bounds(self):
        """Test custom phase bounds."""
        phases = {"C3S": 75.0, "C2S": 15.0, "C3A": 5.0, "C4AF": 5.0}
        # Restrict C3S to [50, 70]
        bounds = {"C3S": (50.0, 70.0), "C2S": (0.0, 100.0), "C3A": (0.0, 100.0), "C4AF": (0.0, 100.0)}
        result = pc.calculate_physical_bound_penalty(phases, phase_bounds=bounds)

        assert result["valid"] is False
        assert any("C3S" in v for v in result["violations"])

    def test_valid_within_bounds(self):
        """Test valid phases within bounds."""
        phases = {"C3S": 65.0, "C2S": 15.0, "C3A": 8.0, "C4AF": 12.0}
        result = pc.calculate_physical_bound_penalty(phases)

        assert result["valid"] is True
        assert result["penalty"] == 0.0


class TestValidatePhasesPrediction:
    """Test comprehensive phase prediction validation."""

    def test_valid_prediction_no_violations(self):
        """Test valid phase prediction with no violations."""
        phases = {"C3S": 65.0, "C2S": 15.0, "C3A": 8.0, "C4AF": 12.0}
        oxides = {"CaO": 68.16, "SiO2": 21.0, "Al2O3": 3.5, "Fe2O3": 2.0}

        result = pc.validate_phase_prediction(phases, input_oxides=oxides)

        assert result["valid"] is True
        assert len(result["warnings"]) == 0

    def test_invalid_prediction_with_violations(self):
        """Test invalid phase prediction with explicit violations."""
        phases = {"C3S": 120.0, "C2S": -10.0, "C3A": 0.0, "C4AF": 0.0}
        oxides = {"CaO": 70.0, "SiO2": 22.0, "Al2O3": 3.0, "Fe2O3": 2.0}

        result = pc.validate_phase_prediction(phases, input_oxides=oxides)

        assert result["valid"] is False
        assert len(result["warnings"]) > 0

    def test_constraint_score_scales(self):
        """Test that constraint_score increases with violations."""
        valid_phases = {"C3S": 65.0, "C2S": 15.0, "C3A": 8.0, "C4AF": 12.0}
        invalid_phases = {"C3S": 120.0, "C2S": 0.0, "C3A": 0.0, "C4AF": 0.0}

        valid_result = pc.validate_phase_prediction(valid_phases)
        invalid_result = pc.validate_phase_prediction(invalid_phases)

        assert valid_result["constraint_score"] < invalid_result["constraint_score"]

    def test_residual_check_included(self):
        """Test that residual_check is included when input_oxides provided."""
        phases = {"C3S": 65.0, "C2S": 15.0, "C3A": 8.0, "C4AF": 12.0}
        oxides = {"CaO": 68.16, "SiO2": 21.0, "Al2O3": 3.5, "Fe2O3": 2.0}

        result = pc.validate_phase_prediction(phases, input_oxides=oxides)

        assert "residual_check" in result
        assert "root_mean_square_residual" in result["residual_check"]


class TestConstraintLossComponents:
    """Test PIML loss component calculation."""

    def test_loss_components_valid_phases(self):
        """Test loss components for valid phases."""
        phases = {"C3S": 65.0, "C2S": 15.0, "C3A": 8.0, "C4AF": 12.0}
        oxides = {"CaO": 68.16, "SiO2": 21.0, "Al2O3": 3.5, "Fe2O3": 2.0}

        losses = pc.constraint_loss_components(phases, input_oxides=oxides)

        # Valid phases should have low losses
        assert losses["L_stoich"] < 2.0
        assert losses["L_bounds"] == 0.0
        assert losses["L_phase_sum"] == 0.0

    def test_loss_components_invalid_phases(self):
        """Test loss components for invalid phases."""
        phases = {"C3S": 120.0, "C2S": -10.0, "C3A": 0.0, "C4AF": 0.0}
        oxides = {"CaO": 90.0, "SiO2": 5.0, "Al2O3": 0.0, "Fe2O3": 0.0}

        losses = pc.constraint_loss_components(phases, input_oxides=oxides)

        # Invalid phases should have high losses
        assert losses["L_bounds"] > 0.0  # Bound penalty for negative phase
        assert losses["L_stoich"] > 0.0  # Stoichiometric residual

    def test_loss_components_without_oxides(self):
        """Test loss components when input_oxides not provided."""
        phases = {"C3S": 65.0, "C2S": 15.0, "C3A": 8.0, "C4AF": 12.0}

        losses = pc.constraint_loss_components(phases)

        # L_stoich should be 0 (no reference oxides)
        assert losses["L_stoich"] == 0.0
        assert "L_bounds" in losses
        assert "L_phase_sum" in losses


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_phases_dict(self):
        """Test handling of empty phases dictionary."""
        phases = {}
        oxides = {"CaO": 0.0, "SiO2": 0.0, "Al2O3": 0.0, "Fe2O3": 0.0}

        result = pc.phase_to_oxide_reconstruction(phases)
        assert all(v == 0.0 for v in result.values())

    def test_all_zero_phases(self):
        """Test handling of all-zero phase fractions."""
        phases = {"C3S": 0.0, "C2S": 0.0, "C3A": 0.0, "C4AF": 0.0}
        result = pc.phase_to_oxide_reconstruction(phases)

        assert all(v == 0.0 for v in result.values())

    def test_free_cao_reconstruction(self):
        """Test reconstruction with Free_CaO phase."""
        phases = {"C3S": 65.0, "C2S": 15.0, "C3A": 8.0, "C4AF": 0.0, "Free_CaO": 2.0}
        oxides = pc.phase_to_oxide_reconstruction(phases)

        # Free_CaO is 100% CaO
        # Total CaO = 65*0.736 + 15*0.652 + 8*0.624 + 0*0.462 + 2*1.0
        expected_cao = 65 * 0.736 + 15 * 0.652 + 8 * 0.624 + 2.0
        assert math.isclose(oxides["CaO"], expected_cao, rel_tol=1e-4)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
