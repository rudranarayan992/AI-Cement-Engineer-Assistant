import pandas as pd

from src.validation.clinker_data_acceptance import validate_clinker_dataset


VALID_RECORD = {
    "Sample_ID": "CLINKER_001",
    "Plant_ID": "PLANT_A",
    "Kiln_ID": "KILN_01",
    "Production_DateTime": "2026-01-10 09:00:00",
    "Sampling_DateTime": "2026-01-10 10:15:00",
    "Raw_Mix_ID": "MIX_001",
    "Kiln_Run_ID": "RUN_001",
    "CaO_wt_pct": 64.7,
    "SiO2_wt_pct": 21.6,
    "Al2O3_wt_pct": 5.3,
    "Fe2O3_wt_pct": 3.1,
    "MgO_wt_pct": 2.1,
    "SO3_wt_pct": 0.9,
    "Na2O_wt_pct": 0.2,
    "K2O_wt_pct": 0.4,
    "LOI_wt_pct": 0.3,
    "Free_CaO_pct": 0.8,
    "C3S_pct": 60.0,
    "C2S_pct": 14.0,
    "C3A_pct": 8.0,
    "C4AF_pct": 10.0,
    "Phase_Method": "XRD",
    "Oxide_Method": "XRF",
    "Free_CaO_Method": "ASTM C114",
    "Lab_ID": "LAB_01",
    "Instrument_ID": "XRF_07",
    "Measurement_DateTime": "2026-01-10 11:00:00",
    "Replicate_ID": "REP_1",
    "Units": "wt%",
    "Basis": "ignited",
}


def test_valid_dataset_passes():
    df = pd.DataFrame([VALID_RECORD])
    result = validate_clinker_dataset(df)
    assert result["status"] == "PASS", result


def test_missing_sample_id_fails():
    df = pd.DataFrame([VALID_RECORD])
    df.loc[0, "Sample_ID"] = None
    result = validate_clinker_dataset(df)
    assert result["status"] == "FAIL"
    assert any("Sample_ID" in reason for reason in result["reasons"])


def test_duplicate_sample_id_fails():
    df = pd.DataFrame([VALID_RECORD, VALID_RECORD.copy()])
    df.loc[1, "Sample_ID"] = "CLINKER_001"
    result = validate_clinker_dataset(df)
    assert result["status"] == "FAIL"
    assert any("Duplicate Sample_ID" in reason for reason in result["reasons"])


def test_impossible_oxide_and_free_cao_values_fail():
    df = pd.DataFrame([VALID_RECORD])
    df.loc[0, "CaO_wt_pct"] = 130.0
    df.loc[0, "Free_CaO_pct"] = -0.5
    result = validate_clinker_dataset(df)
    assert result["status"] == "FAIL"
    assert any("Impossible oxide value" in reason for reason in result["reasons"])
    assert any("Negative Free CaO" in reason for reason in result["reasons"])


def test_phase_sum_problem_and_missing_method_warn_or_fail():
    df = pd.DataFrame([VALID_RECORD])
    df.loc[0, "C3S_pct"] = 40.0
    df.loc[0, "C2S_pct"] = 10.0
    df.loc[0, "C3A_pct"] = 10.0
    df.loc[0, "C4AF_pct"] = 5.0
    df.loc[0, "Phase_Method"] = ""
    result = validate_clinker_dataset(df)
    assert result["status"] in {"FAIL", "WARNING"}
    assert any("Phase sum problem" in reason or "Invalid phase fraction" in reason for reason in result["reasons"])


def test_future_timestamp_warns():
    df = pd.DataFrame([VALID_RECORD])
    df.loc[0, "Measurement_DateTime"] = "2099-01-01 00:00:00"
    result = validate_clinker_dataset(df)
    assert result["status"] in {"WARNING", "FAIL"}
    assert any("Suspicious future information" in reason for reason in result["reasons"])


def test_missing_traceability_fails():
    df = pd.DataFrame([VALID_RECORD])
    df.loc[0, "Raw_Mix_ID"] = None
    result = validate_clinker_dataset(df)
    assert result["status"] == "FAIL"
    assert any("Missing traceability linkage" in reason for reason in result["reasons"])
