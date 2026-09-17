import pandas as pd

from src.pipeline.raw_material_chemistry_track import (
    DEFAULT_RAW_MEAL_RECIPE,
    build_calculated_raw_meal,
    export_calculated_raw_meal_csv,
)


def test_build_calculated_raw_meal_has_valid_chemistry_scope():
    result = build_calculated_raw_meal()

    assert result["track"] == "12K_raw_material_to_raw_meal_chemistry"
    assert result["data_status"] == "calculated"
    assert "clinker" not in result["scientific_scope"].lower()
    assert "chemistry-only" in result["restriction"].lower()
    assert "target" in result["restriction"].lower() or "prediction" in result["restriction"].lower()
    assert abs(sum(result["mix_proportions"].values()) - 100.0) < 1e-6
    assert result["mass_balance_ok"] is True
    assert 0.0 < result["moduli"]["LSF"] < 200.0
    assert 0.0 < result["moduli"]["SM"] < 10.0
    assert 0.0 < result["moduli"]["AM"] < 10.0
    assert set(DEFAULT_RAW_MEAL_RECIPE).issubset(set(result["mix_proportions"]))


def test_export_calculated_raw_meal_csv_writes_derived_results(tmp_path):
    out_path = tmp_path / "track_c_raw_meal.csv"
    df = export_calculated_raw_meal_csv(output_csv=out_path)

    assert out_path.exists()
    assert df.shape[0] == 1
    assert df.iloc[0]["data_status"] == "calculated"
    assert df.iloc[0]["track"] == "12K_raw_material_to_raw_meal_chemistry"
    assert "CaO_pct" in df.columns
    assert "LSF" in df.columns
    assert "SM" in df.columns
    assert "AM" in df.columns
