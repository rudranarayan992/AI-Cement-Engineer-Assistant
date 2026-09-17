"""Unit tests for prediction modules (free CaO and strength)."""

from __future__ import annotations

import pytest
from src.prediction.free_caO_predictor import predict_free_ca_o, summarize_prediction
from src.prediction.strength_predictor import predict_compressive_strength

def test_predict_free_ca_o_normal():
    inputs = {
        "Raw_CaO": 43.5,
        "Raw_SiO2": 13.8,
        "Raw_Al2O3": 3.2,
        "Raw_Fe2O3": 2.1,
        "Kiln_Temp_C": 1420.0,
        "Fineness_90um_pct": 12.5,
    }
    result = predict_free_ca_o(inputs)
    assert result["target"] == "Free CaO"
    assert 0.2 <= result["prediction"] <= 5.0
    assert result["confidence"] > 0.5
    assert len(result["drivers"]) > 0

def test_predict_free_ca_o_ood():
    inputs = {
        "Raw_CaO": 48.0, # High LSF
        "Raw_SiO2": 10.0,
        "Raw_Al2O3": 2.0,
        "Raw_Fe2O3": 1.5,
        "Kiln_Temp_C": 1250.0, # Low Kiln Temp
        "Fineness_90um_pct": 20.0, # Coarse meal
    }
    result = predict_free_ca_o(inputs)
    assert len(result["ood_warnings"]) > 0
    assert result["confidence"] < 0.8

def test_summarize_prediction():
    res = {"target": "Free CaO", "prediction": 1.15, "unit": "%", "confidence": 0.92, "source": "XGBoost"}
    summary = summarize_prediction(res)
    assert "1.15 %" in summary

def test_predict_compressive_strength():
    inputs = {
        "C3S_pct": 58.5,
        "C2S_pct": 16.2,
        "C3A_pct": 7.8,
        "C4AF_pct": 9.4,
        "Free_CaO_pct": 1.2,
        "Blaine_cm2g": 3600.0,
        "Gypsum_SO3_pct": 2.8,
        "WC_Ratio": 0.48,
    }
    res = predict_compressive_strength(inputs)
    assert res["strength_3d_MPa"] < res["strength_7d_MPa"] < res["strength_28d_MPa"]
    assert res["strength_28d_MPa"] > 30.0
    assert "Grade" in res["grade_classification"]
