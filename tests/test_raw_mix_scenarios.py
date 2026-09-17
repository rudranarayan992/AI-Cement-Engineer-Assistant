import math

import pandas as pd

from src.optimization.raw_mix_scenarios import (
    DEFAULT_BASELINE_RECIPE,
    build_baseline_scenario,
    calculate_raw_mix_scenario,
    check_engineering_constraints,
    compare_scenarios,
    deterministic_sensitivity_analysis,
    rank_feasible_scenarios,
    validate_raw_mix_recipe,
)


MATERIALS = pd.read_csv("data/raw_materials/raw_materials_database.csv")


def test_valid_recipe_calculates_expected_baseline():
    result = build_baseline_scenario(MATERIALS)

    assert result["valid"] is True
    assert abs(result["chemistry"]["CaO"] - 42.39) < 0.1
    assert abs(result["moduli"]["LSF"] - 87.05) < 0.15
    assert abs(result["moduli"]["SM"] - 2.086) < 0.05
    assert abs(result["moduli"]["AM"] - 0.902) < 0.05


def test_invalid_proportion_sum_is_rejected():
    invalid_recipe = {"LS_001": 70.0, "CLAY_001": 14.0, "SAND_001": 5.0, "IRON_001": 3.0}
    validation = validate_raw_mix_recipe(MATERIALS, invalid_recipe)

    assert validation["valid"] is False
    assert any("outside the permitted tolerance" in error for error in validation["errors"])


def test_negative_proportion_is_rejected():
    invalid_recipe = {"LS_001": 78.0, "CLAY_001": -1.0, "SAND_001": 15.0, "IRON_001": 8.0}
    validation = validate_raw_mix_recipe(MATERIALS, invalid_recipe)

    assert validation["valid"] is False
    assert any("negative" in error.lower() for error in validation["errors"])


def test_missing_chemistry_is_not_silently_zeroed():
    df = MATERIALS.copy()
    df.loc[df["Sample_ID"] == "CLAY_001", "SiO2"] = float("nan")
    validation = validate_raw_mix_recipe(df, DEFAULT_BASELINE_RECIPE)

    assert validation["valid"] is False
    assert any("Missing required chemistry" in error for error in validation["errors"])


def test_invalid_basis_is_rejected():
    result = calculate_raw_mix_scenario(MATERIALS, DEFAULT_BASELINE_RECIPE, basis="clinker")

    assert result["valid"] is False
    assert any("Invalid basis" in item for item in result["errors"])


def test_repeatability_is_deterministic():
    a = calculate_raw_mix_scenario(MATERIALS, DEFAULT_BASELINE_RECIPE)
    b = calculate_raw_mix_scenario(MATERIALS, DEFAULT_BASELINE_RECIPE)

    assert a["chemistry"] == b["chemistry"]
    assert a["moduli"] == b["moduli"]


def test_baseline_scenario_contains_provenance():
    result = calculate_raw_mix_scenario(MATERIALS, DEFAULT_BASELINE_RECIPE)

    assert result["provenance"]["source_dataset"].endswith("raw_materials_database.csv")
    assert result["provenance"]["input_data_status"] == "MEASURED INPUT"
    assert result["provenance"]["data_status"] == "CALCULATED OUTPUT"
    assert result["provenance"]["basis"] == "as_received"
    assert result["provenance"]["recipe"] == DEFAULT_BASELINE_RECIPE


def test_scenario_comparison_reports_changes():
    baseline = calculate_raw_mix_scenario(MATERIALS, DEFAULT_BASELINE_RECIPE)
    scenario_recipe = {"LS_001": 76.0, "CLAY_001": 15.0, "SAND_001": 5.0, "IRON_001": 4.0}
    scenario = calculate_raw_mix_scenario(MATERIALS, scenario_recipe)
    changes = compare_scenarios(baseline, scenario)

    assert "CaO" in changes["changes"]
    assert "LSF" in changes["changes"]
    assert "absolute_change" in changes["changes"]["CaO"]
    assert "percentage_point_change" in changes["changes"]["LSF"]


def test_sensitivity_analysis_is_deterministic_and_labeled():
    result = deterministic_sensitivity_analysis(MATERIALS, DEFAULT_BASELINE_RECIPE)

    assert result["valid"] is True
    assert result["label"] == "DETERMINISTIC CHEMISTRY SENSITIVITY"
    assert len(result["sensitivity_by_material"]) > 0
    assert all(item["label"] == "DETERMINISTIC CHEMISTRY SENSITIVITY" for item in result["sensitivity_by_material"])


def test_constraint_evaluation_pass_and_fail():
    baseline = calculate_raw_mix_scenario(MATERIALS, DEFAULT_BASELINE_RECIPE)
    pass_result = check_engineering_constraints(
        baseline,
        lsf_min=80.0,
        lsf_max=100.0,
        sm_min=1.5,
        sm_max=3.0,
        am_min=0.5,
        am_max=1.5,
    )
    fail_result = check_engineering_constraints(
        baseline,
        lsf_min=90.0,
        lsf_max=90.1,
        sm_min=2.5,
        sm_max=2.6,
        am_min=0.9,
        am_max=1.0,
    )

    assert pass_result["overall_status"] == "PASS"
    assert fail_result["overall_status"] in {"WARNING", "FAIL"}


def test_provenance_retains_traceability_metadata():
    result = calculate_raw_mix_scenario(MATERIALS, DEFAULT_BASELINE_RECIPE)
    provenance = result["provenance"]

    assert provenance["source_material_ids"] == ["LS_001", "CLAY_001", "SAND_001", "IRON_001"]
    assert "calculation_timestamp_utc" in provenance
    assert provenance["calculation_method"] == "weighted oxide mass balance"


def test_no_silent_zero_replacement_for_missing_chemistry():
    df = MATERIALS.copy()
    df.loc[df["Sample_ID"] == "IRON_001", "Fe2O3"] = float("nan")
    result = calculate_raw_mix_scenario(df, DEFAULT_BASELINE_RECIPE)

    assert result["valid"] is False
    assert any("Missing required chemistry" in item for item in result["errors"])


def test_rank_feasible_scenarios_assigns_order_without_ml_claim():
    baseline = calculate_raw_mix_scenario(MATERIALS, DEFAULT_BASELINE_RECIPE)
    scenarioA = calculate_raw_mix_scenario(MATERIALS, {"LS_001": 80.0, "CLAY_001": 12.0, "SAND_001": 5.0, "IRON_001": 3.0})
    scenarioB = calculate_raw_mix_scenario(MATERIALS, {"LS_001": 75.0, "CLAY_001": 16.0, "SAND_001": 5.0, "IRON_001": 4.0})

    ranked = rank_feasible_scenarios(
        [baseline, scenarioA, scenarioB],
        baseline,
        lsf_min=80.0,
        lsf_max=100.0,
        sm_min=1.5,
        sm_max=3.0,
        am_min=0.5,
        am_max=1.5,
    )

    assert len(ranked) >= 1
    assert all(item["distance_from_baseline"] >= 0 for item in ranked)
