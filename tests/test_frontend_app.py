import pandas as pd

from app.streamlit_app import (
    PROJECT_STATUS,
    answer_engineering_question,
    compute_recipe_result,
    get_data_provenance_table,
)


def test_project_status_honestly_blocks_clinker_ml():
    assert PROJECT_STATUS["CLINKER ML"] == "BLOCKED"
    assert PROJECT_STATUS["REAL CLINKER DATA"] == "REQUIRED"


def test_recipe_result_validates_raw_mix_engineering():
    materials = pd.read_csv("data/raw_materials/raw_materials_database.csv")
    result = compute_recipe_result(materials, {"LS_001": 78.0, "CLAY_001": 14.0, "SAND_001": 5.0, "IRON_001": 3.0})

    assert result["valid"] is True
    assert result["provenance"]["input_data_status"] == "MEASURED INPUT"
    assert set(["LSF", "SM", "AM"]).issubset(result["moduli"].keys())
    assert result["mass_balance_ok"] is True


def test_copilot_refuses_fake_real_clinker_prediction():
    response = answer_engineering_question("Predict Free CaO")

    assert "unavailable" in response.lower()
    assert "synthetic" in response.lower() or "synthetic/generated" in response.lower()
    assert "verified measured clinker target" in response.lower()


def test_provenance_table_makes_dataset_status_clear():
    df = get_data_provenance_table()

    assert "raw_materials_database.csv" in set(df["Dataset"])
    assert "clinker targets" in set(df["Dataset"])
    assert "BLOCKED" in set(df["Status"]) 
