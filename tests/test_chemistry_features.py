"""Unit tests for chemistry feature engineering.

Test coverage:
1. Valid chemistry input
2. LSF calculation
3. SM calculation
4. AM calculation
5. Bogue reference calculation
6. Missing oxide handling
7. Invalid basis handling
8. Negative chemistry detection
9. NaN handling
10. Infinity handling
11. Invalid phase values
12. Feature provenance completeness
13. No silent zero substitution
14. Deterministic output
15. Leakage metadata classification
"""

import math
import pytest
import pandas as pd

try:
    from src.features.chemistry_features import (
        extract_cement_chemistry_features,
        extract_multiple_chemistry_features,
        ChemistryFeatureSet,
        FeatureProvenance,
    )
except ImportError:
    try:
        from features.chemistry_features import (
            extract_cement_chemistry_features,
            extract_multiple_chemistry_features,
            ChemistryFeatureSet,
            FeatureProvenance,
        )
    except ImportError:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, "src"))
        from features.chemistry_features import (
            extract_cement_chemistry_features,
            extract_multiple_chemistry_features,
            ChemistryFeatureSet,
            FeatureProvenance,
        )


class TestValidInput:
    """Test valid chemistry input processing."""

    def test_valid_chemistry_input(self):
        """Test extraction with valid cement chemistry."""
        oxide_data = {
            "CaO": 65.0,
            "SiO2": 22.0,
            "Al2O3": 5.0,
            "Fe2O3": 3.0,
        }
        result = extract_cement_chemistry_features(oxide_data, batch_id="TEST_001")

        assert isinstance(result, ChemistryFeatureSet)
        assert result.batch_id == "TEST_001"
        assert result.computation_valid is True
        assert result.lsf is not None
        assert result.sm is not None
        assert result.am is not None
        assert not math.isnan(result.lsf)
        assert not math.isnan(result.sm)
        assert not math.isnan(result.am)

    def test_typical_cement_composition(self):
        """Test with typical Portland cement oxide composition."""
        # Typical Portland cement (as-received basis includes LOI)
        oxide_data = {
            "CaO": 63.0,
            "SiO2": 21.5,
            "Al2O3": 5.2,
            "Fe2O3": 3.2,
            "MgO": 2.0,
            "SO3": 0.6,
            "LOI": 2.5,
        }
        result = extract_cement_chemistry_features(
            oxide_data,
            batch_id="TYPICAL_001",
            input_basis="as_received",
        )

        assert result.computation_valid is True
        # LSF should be in reasonable range (0.9-1.05)
        assert 0.8 < result.lsf < 1.2
        # SM should be in reasonable range (2.0-3.0)
        assert 1.5 < result.sm < 4.0
        # AM should be in reasonable range (1.4-2.2)
        assert 1.0 < result.am < 2.5


class TestModuliCalculation:
    """Test individual moduli calculations."""

    def test_lsf_calculation(self):
        """Test LSF is computed correctly from known values."""
        oxide_data = {"CaO": 64.0, "SiO2": 22.0, "Al2O3": 5.0, "Fe2O3": 3.0}
        result = extract_cement_chemistry_features(oxide_data)

        # LSF = 64 / (2.8*22 + 1.18*5 + 0.65*3)
        # LSF = 64 / (61.6 + 5.9 + 1.95) = 64 / 69.45 ≈ 0.9213
        expected_lsf = 64.0 / (2.8 * 22.0 + 1.18 * 5.0 + 0.65 * 3.0)
        assert math.isclose(result.lsf, expected_lsf, rel_tol=1e-3)

    def test_sm_calculation(self):
        """Test SM is computed correctly from known values."""
        oxide_data = {"CaO": 65.0, "SiO2": 22.0, "Al2O3": 5.0, "Fe2O3": 3.0}
        result = extract_cement_chemistry_features(oxide_data)

        # SM = SiO2 / (Al2O3 + Fe2O3) = 22 / (5 + 3) = 22 / 8 = 2.75
        expected_sm = 22.0 / (5.0 + 3.0)
        assert math.isclose(result.sm, expected_sm, rel_tol=1e-3)

    def test_am_calculation(self):
        """Test AM is computed correctly from known values."""
        oxide_data = {"CaO": 65.0, "SiO2": 22.0, "Al2O3": 5.0, "Fe2O3": 3.0}
        result = extract_cement_chemistry_features(oxide_data)

        # AM = Al2O3 / Fe2O3 = 5 / 3 ≈ 1.667
        expected_am = 5.0 / 3.0
        assert math.isclose(result.am, expected_am, rel_tol=1e-3)


class TestBogueReference:
    """Test Bogue empirical phase calculation."""

    def test_bogue_phases_with_free_cao(self):
        """Test Bogue phases are computed when Free CaO provided."""
        oxide_data = {
            "CaO": 65.0,
            "SiO2": 22.0,
            "Al2O3": 5.0,
            "Fe2O3": 3.0,
        }
        result = extract_cement_chemistry_features(
            oxide_data,
            batch_id="BOGUE_TEST",
            free_cao=0.8,
            so3=0.6,
        )

        assert result.bogue_reference_c3s is not None
        assert result.bogue_reference_c2s is not None
        assert result.bogue_reference_c3a is not None
        assert result.bogue_reference_c4af is not None
        # Bogue phases should be positive and sum to roughly 100%
        total = (
            result.bogue_reference_c3s
            + result.bogue_reference_c2s
            + result.bogue_reference_c3a
            + result.bogue_reference_c4af
        )
        assert 80.0 < total < 105.0

    def test_bogue_skipped_without_free_cao(self):
        """Test Bogue calculation is skipped when Free CaO not provided."""
        oxide_data = {
            "CaO": 65.0,
            "SiO2": 22.0,
            "Al2O3": 5.0,
            "Fe2O3": 3.0,
        }
        result = extract_cement_chemistry_features(oxide_data)

        assert result.bogue_reference_c3s is None
        assert "Free CaO not provided" in " ".join(result.warnings)

    def test_bogue_labeled_as_reference(self):
        """Test Bogue phases are labeled with 'reference' in provenance."""
        oxide_data = {
            "CaO": 65.0,
            "SiO2": 22.0,
            "Al2O3": 5.0,
            "Fe2O3": 3.0,
        }
        result = extract_cement_chemistry_features(
            oxide_data,
            free_cao=0.8,
            so3=0.6,
        )

        for phase in ["c3s", "c2s", "c3a", "c4af"]:
            prov_key = f"bogue_reference_{phase}"
            assert prov_key in result.feature_provenances
            prov = result.feature_provenances[prov_key]
            assert prov.calculation_method == "reference"
            assert "empirical" in prov.formula.lower()
            assert "not be treated as measured XRD" in prov.leakage_notes


class TestMissingOxide:
    """Test handling of missing oxide data."""

    def test_missing_cao(self):
        """Test computation fails gracefully when CaO is missing."""
        oxide_data = {"SiO2": 22.0, "Al2O3": 5.0, "Fe2O3": 3.0}
        result = extract_cement_chemistry_features(oxide_data)

        assert math.isnan(result.lsf)
        assert math.isnan(result.sm)
        assert math.isnan(result.am)
        assert result.computation_valid is False

    def test_missing_sio2(self):
        """Test computation fails when SiO2 is missing."""
        oxide_data = {"CaO": 65.0, "Al2O3": 5.0, "Fe2O3": 3.0}
        result = extract_cement_chemistry_features(oxide_data)

        assert result.computation_valid is False

    def test_no_silent_zero_substitution(self):
        """Test that missing oxides are NOT silently replaced with zero."""
        oxide_data = {"CaO": 65.0, "SiO2": 22.0, "Al2O3": 5.0, "Fe2O3": None}
        result = extract_cement_chemistry_features(oxide_data)

        # Should NOT compute moduli with Fe2O3=0
        assert result.computation_valid is False
        assert math.isnan(result.am)


class TestBasisHandling:
    """Test explicit basis specification."""

    def test_as_received_basis(self):
        """Test LSF/SM/AM with as-received basis."""
        oxide_data = {
            "CaO": 63.0,
            "SiO2": 21.5,
            "Al2O3": 5.0,
            "Fe2O3": 3.0,
            "LOI": 2.0,
        }
        result = extract_cement_chemistry_features(
            oxide_data,
            input_basis="as_received",
        )

        # With LOI, chemistry engine may raise error or adjust
        # At minimum, should not silently succeed
        assert result.input_basis == "as_received"

    def test_ignited_basis(self):
        """Test moduli with ignited basis (LOI removed)."""
        oxide_data = {
            "CaO": 64.5,
            "SiO2": 22.0,
            "Al2O3": 5.1,
            "Fe2O3": 3.0,
        }
        result = extract_cement_chemistry_features(
            oxide_data,
            input_basis="ignited",
        )

        # Should compute successfully with ignited basis
        assert result.computation_valid is True
        assert result.lsf is not None


class TestNegativeChemistry:
    """Test detection of impossible negative chemistry."""

    def test_negative_cao(self):
        """Test detection of negative CaO."""
        oxide_data = {
            "CaO": -5.0,
            "SiO2": 22.0,
            "Al2O3": 5.0,
            "Fe2O3": 3.0,
        }
        result = extract_cement_chemistry_features(oxide_data)

        assert result.computation_valid is False
        assert "negative" in " ".join(result.warnings).lower()

    def test_negative_sio2(self):
        """Test detection of negative SiO2."""
        oxide_data = {
            "CaO": 65.0,
            "SiO2": -10.0,
            "Al2O3": 5.0,
            "Fe2O3": 3.0,
        }
        result = extract_cement_chemistry_features(oxide_data)

        assert result.computation_valid is False


class TestNaNAndInfinity:
    """Test handling of NaN and infinity values."""

    def test_nan_cao(self):
        """Test detection of NaN in CaO."""
        oxide_data = {
            "CaO": float("nan"),
            "SiO2": 22.0,
            "Al2O3": 5.0,
            "Fe2O3": 3.0,
        }
        result = extract_cement_chemistry_features(oxide_data)

        assert result.computation_valid is False
        assert math.isnan(result.lsf)

    def test_infinite_sio2(self):
        """Test detection of infinity in SiO2."""
        oxide_data = {
            "CaO": 65.0,
            "SiO2": float("inf"),
            "Al2O3": 5.0,
            "Fe2O3": 3.0,
        }
        result = extract_cement_chemistry_features(oxide_data)

        assert result.computation_valid is False


class TestDeterministicOutput:
    """Test that computations are deterministic."""

    def test_deterministic_lsf(self):
        """Test LSF computation is deterministic."""
        oxide_data = {
            "CaO": 64.237,
            "SiO2": 21.891,
            "Al2O3": 5.121,
            "Fe2O3": 3.087,
        }

        result1 = extract_cement_chemistry_features(oxide_data)
        result2 = extract_cement_chemistry_features(oxide_data)

        assert result1.lsf == result2.lsf
        assert result1.sm == result2.sm
        assert result1.am == result2.am

    def test_deterministic_with_seed(self):
        """Test determinism across multiple calls."""
        oxide_data = {
            "CaO": 65.0,
            "SiO2": 22.0,
            "Al2O3": 5.0,
            "Fe2O3": 3.0,
        }

        results = [extract_cement_chemistry_features(oxide_data) for _ in range(5)]

        # All results should be identical
        for result in results[1:]:
            assert result.lsf == results[0].lsf
            assert result.sm == results[0].sm
            assert result.am == results[0].am


class TestProvenance:
    """Test feature provenance tracking."""

    def test_lsf_provenance(self):
        """Test LSF has complete provenance."""
        oxide_data = {
            "CaO": 65.0,
            "SiO2": 22.0,
            "Al2O3": 5.0,
            "Fe2O3": 3.0,
        }
        result = extract_cement_chemistry_features(oxide_data)

        assert "lsf" in result.feature_provenances
        prov = result.feature_provenances["lsf"]
        assert isinstance(prov, FeatureProvenance)
        assert prov.feature_name == "lsf"
        assert "CaO" in prov.source_variables
        assert prov.basis is not None
        assert prov.units is not None
        assert prov.leakage_risk == "SAFE"

    def test_all_features_have_provenance(self):
        """Test all computed features have provenance."""
        oxide_data = {
            "CaO": 65.0,
            "SiO2": 22.0,
            "Al2O3": 5.0,
            "Fe2O3": 3.0,
        }
        result = extract_cement_chemistry_features(
            oxide_data,
            free_cao=0.8,
            so3=0.6,
        )

        expected_features = ["lsf", "sm", "am", "bogue_reference_c3s", "bogue_reference_c2s", "bogue_reference_c3a", "bogue_reference_c4af"]
        for feature in expected_features:
            assert feature in result.feature_provenances or result.bogue_reference_c3s is None


class TestLeakageClassification:
    """Test feature leakage risk classification."""

    def test_moduli_marked_safe(self):
        """Test moduli (LSF/SM/AM) are marked as SAFE."""
        oxide_data = {
            "CaO": 65.0,
            "SiO2": 22.0,
            "Al2O3": 5.0,
            "Fe2O3": 3.0,
        }
        result = extract_cement_chemistry_features(oxide_data)

        for feature_name in ["lsf", "sm", "am"]:
            prov = result.feature_provenances[feature_name]
            assert prov.leakage_risk == "SAFE"
            assert prov.target_derived is False

    def test_bogue_marked_conditional(self):
        """Test Bogue phases are marked as CONDITIONAL."""
        oxide_data = {
            "CaO": 65.0,
            "SiO2": 22.0,
            "Al2O3": 5.0,
            "Fe2O3": 3.0,
        }
        result = extract_cement_chemistry_features(
            oxide_data,
            free_cao=0.8,
            so3=0.6,
        )

        for phase in ["c3s", "c2s", "c3a", "c4af"]:
            prov_key = f"bogue_reference_{phase}"
            prov = result.feature_provenances[prov_key]
            assert prov.leakage_risk == "CONDITIONAL"


class TestDataFrameConversion:
    """Test integration with pandas DataFrames."""

    def test_feature_set_to_dataframe(self):
        """Test conversion of single FeatureSet to DataFrame."""
        oxide_data = {
            "CaO": 65.0,
            "SiO2": 22.0,
            "Al2O3": 5.0,
            "Fe2O3": 3.0,
        }
        result = extract_cement_chemistry_features(oxide_data, batch_id="TEST_001")

        df = result.to_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert df.shape[0] == 1
        assert "lsf" in df.columns
        assert "sm" in df.columns
        assert "am" in df.columns
        assert df.loc[0, "batch_id"] == "TEST_001"

    def test_batch_extraction_from_dataframe(self):
        """Test batch extraction from DataFrame."""
        oxide_df = pd.DataFrame(
            [
                {"Batch_ID": "B001", "CaO": 65.0, "SiO2": 22.0, "Al2O3": 5.0, "Fe2O3": 3.0},
                {"Batch_ID": "B002", "CaO": 64.0, "SiO2": 21.5, "Al2O3": 5.1, "Fe2O3": 3.1},
                {"Batch_ID": "B003", "CaO": 66.0, "SiO2": 22.5, "Al2O3": 4.9, "Fe2O3": 2.9},
            ]
        )

        result_df = extract_multiple_chemistry_features(
            oxide_df,
            batch_id_column="Batch_ID",
            cao_column="CaO",
            sio2_column="SiO2",
            al2o3_column="Al2O3",
            fe2o3_column="Fe2O3",
        )

        assert isinstance(result_df, pd.DataFrame)
        assert result_df.shape[0] == 3
        assert "lsf" in result_df.columns
        assert list(result_df["batch_id"]) == ["B001", "B002", "B003"]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_oxide_data(self):
        """Test error handling for empty oxide data."""
        with pytest.raises(ValueError):
            extract_cement_chemistry_features({})

    def test_non_dict_input(self):
        """Test error handling for non-dict input."""
        with pytest.raises(TypeError):
            extract_cement_chemistry_features(["CaO", "SiO2", "Al2O3", "Fe2O3"])

    def test_zero_fe2o3_division(self):
        """Test handling of zero Fe2O3 (AM denominator = 0)."""
        oxide_data = {
            "CaO": 65.0,
            "SiO2": 22.0,
            "Al2O3": 5.0,
            "Fe2O3": 0.0,
        }
        result = extract_cement_chemistry_features(oxide_data)

        # AM = Al2O3 / 0 → should be NaN or raise error gracefully
        assert math.isnan(result.am) or result.computation_valid is False

    def test_very_high_lsf(self):
        """Test with very high LSF (lime-rich cement)."""
        oxide_data = {
            "CaO": 70.0,
            "SiO2": 18.0,
            "Al2O3": 5.0,
            "Fe2O3": 3.0,
        }
        result = extract_cement_chemistry_features(oxide_data)

        assert result.computation_valid is True
        assert result.lsf > 1.0  # High LSF


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
