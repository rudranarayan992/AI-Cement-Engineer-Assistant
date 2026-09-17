"""Interface-level tests for the future cement/clinker ML architecture."""

from datetime import datetime

import pytest

from src.future_ml.cement_ml_architecture import (
    ChronologicalSplitConfig,
    DEFAULT_FEATURE_POLICY,
    MLPrediction,
    OODResult,
    PredictionMetadata,
    RawMixRecord,
    TargetDefinition,
    TemporalAlignmentConfig,
    UncertaintyResult,
    FUTURE_TARGET_TAXONOMY,
    validate_phase_prediction,
    reconstruct_oxide_from_phases,
)


def test_target_schema_validation_accepts_measured_ground_truth():
    target = TargetDefinition(
        name="Free_CaO",
        unit="%",
        measurement_method="Lab analysis",
        ground_truth_source="MEASURED_LAB",
        prediction_stage="clinker_production",
        online_suitable=True,
    )
    target.validate_for_training()
    assert target.is_measured_ground_truth() is True


def test_synthetic_target_rejected_for_training():
    target = TargetDefinition(
        name="Synthetic_Free_CaO",
        unit="%",
        measurement_method="Synthetic generator",
        ground_truth_source="SYNTHETIC",
        prediction_stage="demo",
        online_suitable=False,
    )
    with pytest.raises(ValueError):
        target.validate_for_training()


def test_bogue_target_is_rejected_for_training():
    target = TargetDefinition(
        name="Bogue_C3S",
        unit="%",
        measurement_method="Calculated Bogue estimate",
        ground_truth_source="BOGUE_CALCULATED",
        prediction_stage="reference",
        online_suitable=False,
    )
    with pytest.raises(ValueError):
        target.validate_for_training()


def test_feature_policy_separates_online_and_post_production_features():
    online = DEFAULT_FEATURE_POLICY.online_features()
    offline = DEFAULT_FEATURE_POLICY.post_production_features()
    assert any(feature.name == "LSF" for feature in online)
    assert any(feature.name == "clinker_xrd_phase" for feature in offline)
    assert all(feature.online_eligible for feature in online)
    assert all(not feature.online_eligible for feature in offline)


def test_provenance_propagates_through_raw_mix_record():
    record = RawMixRecord(
        plant_id="P01",
        kiln_id="KILN_2",
        batch_id="BATCH_0005",
        raw_mix_id="RM_005",
        material_proportions={"LS_001": 0.74, "CLAY_001": 0.26},
        lsf=0.96,
        sm=2.45,
        am=1.72,
    )
    assert record.plant_id == "P01"
    assert record.raw_mix_id == "RM_005"
    assert record.lsf == 0.96


def test_temporal_alignment_requires_explicit_residence_time():
    cfg = TemporalAlignmentConfig()
    with pytest.raises(ValueError):
        cfg.validate()


def test_chronological_split_config_validates_ordering():
    cfg = ChronologicalSplitConfig(
        train_end=datetime(2024, 1, 31),
        validation_end=datetime(2024, 3, 31),
        test_end=datetime(2024, 6, 30),
    )
    cfg.validate()
    ranges = cfg.build_ranges()
    assert set(ranges) == {"train", "validation", "test"}


def test_phase_validation_interface_accepts_valid_prediction():
    result = validate_phase_prediction({"C3S": 60.0, "C2S": 18.0, "C3A": 8.0, "C4AF": 11.0})
    assert result.chemistry_valid is True
    assert result.phase_valid is True


def test_stoichiometric_reconstruction_requires_explicit_config():
    result = reconstruct_oxide_from_phases({"C3S": 60.0, "C2S": 20.0})
    assert result.status == "UNAVAILABLE"
    assert "Stoichiometric reconstruction requires explicit" in result.notes


def test_prediction_metadata_schema_is_valid():
    metadata = PredictionMetadata(
        model_id="future_model_001",
        target="Free_CaO",
        target_measurement_method="MEASURED_LAB",
        features=["LSF", "SM", "AM", "Feed_Rate_tph"],
        feature_policy=["LEVEL_A_ONLINE_CONTROL"],
        plant_id="P01",
        algorithm="ridge",
        known_limitations=["Requires real industrial data"],
    )
    assert metadata.target == "Free_CaO"
    assert metadata.model_id == "future_model_001"


def test_ood_and_uncertainty_metadata_interfaces():
    ood = OODResult(status="OK", method="mahalanobis", threshold=3.0)
    uncertainty = UncertaintyResult(value=0.08, method="ensemble", calibrated=False)
    assert ood.status == "OK"
    assert uncertainty.method == "ensemble"


def test_prediction_result_interface_works():
    prediction = MLPrediction(prediction=0.95, uncertainty=0.1, ood_status="SAFE", warning=None)
    assert prediction.prediction == 0.95
    assert prediction.ood_status == "SAFE"


def test_future_taxonomy_contains_only_measured_targets_for_training():
    training_targets = FUTURE_TARGET_TAXONOMY.training_targets()
    names = {target.name for target in training_targets}
    assert "Free_CaO" in names
    assert "C3S" in names
    assert "C3A" in names
    assert "Compressive_Strength_28d" in names
    assert not any(target.name == "Bogue_C3S" for target in training_targets)
