"""Free CaO prediction module utilizing trained ML models with fallback heuristics and OOD detection."""

from __future__ import annotations

import os
import joblib
import pandas as pd
import numpy as np
from typing import Any, Dict, List
from src.chemistry.clinker_chemistry import calculate_clinker_ratios

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "models",
    "free_cao_xgb.joblib"
)

_cached_model_data = None

def _get_model():
    global _cached_model_data
    if _cached_model_data is None and os.path.exists(MODEL_PATH):
        try:
            _cached_model_data = joblib.load(MODEL_PATH)
        except Exception:
            _cached_model_data = False
    return _cached_model_data

def predict_free_ca_o(features: Dict[str, float]) -> Dict[str, Any]:
    """Predict Free CaO (%) from raw/clinker oxides and kiln process inputs.

    Uses trained XGBoost model if available, otherwise falls back to chemistry domain heuristics.
    Includes Out-Of-Distribution (OOD) checks and top feature drivers.
    """
    model_data = _get_model()

    # Extract inputs with defaults
    raw_cao = float(features.get("Raw_CaO", features.get("CaO", 43.5)))
    raw_sio2 = float(features.get("Raw_SiO2", features.get("SiO2", 13.5)))
    raw_al2o3 = float(features.get("Raw_Al2O3", features.get("Al2O3", 3.2)))
    raw_fe2o3 = float(features.get("Raw_Fe2O3", features.get("Fe2O3", 2.1)))
    kiln_temp = float(features.get("Kiln_Temp_C", features.get("kiln_temperature_c", 1420.0)))
    feed_rate = float(features.get("Feed_Rate_tph", 180.0))
    fan_speed = float(features.get("Fan_Speed_rpm", 1100.0))
    sec_air_temp = float(features.get("Sec_Air_Temp_C", 920.0))
    fineness_90um = float(features.get("Fineness_90um_pct", 12.5))

    # Calculate clinker basis oxides & moduli
    clinker_cao = raw_cao * 1.55
    clinker_sio2 = raw_sio2 * 1.55
    clinker_al2o3 = raw_al2o3 * 1.55
    clinker_fe2o3 = raw_fe2o3 * 1.55

    ratios = calculate_clinker_ratios({
        "CaO": clinker_cao,
        "SiO2": clinker_sio2,
        "Al2O3": clinker_al2o3,
        "Fe2O3": clinker_fe2o3
    })
    lsf = ratios["LSF"]
    sm = ratios["SM"]
    am = ratios["AM"]

    # Check Out-of-Distribution (OOD)
    ood_warnings = []
    if lsf < 0.85 or lsf > 1.08:
        ood_warnings.append(f"LSF ({lsf:.3f}) is outside typical kiln operation range (0.88 - 1.05).")
    if kiln_temp < 1300 or kiln_temp > 1550:
        ood_warnings.append(f"Kiln temperature ({kiln_temp:.1f}°C) is outside safe burning zone (1350 - 1500°C).")
    if fineness_90um > 18.0:
        ood_warnings.append(f"Raw meal 90µm residue ({fineness_90um:.1f}%) is excessively coarse.")

    confidence = 0.92 if not ood_warnings else max(0.45, 0.92 - 0.20 * len(ood_warnings))

    if model_data and isinstance(model_data, dict):
        model = model_data["model"]
        feature_names = model_data["features"]
        row_dict = {
            "Raw_CaO": raw_cao, "Raw_SiO2": raw_sio2, "Raw_Al2O3": raw_al2o3, "Raw_Fe2O3": raw_fe2o3,
            "Clinker_CaO": clinker_cao, "Clinker_SiO2": clinker_sio2, "Clinker_Al2O3": clinker_al2o3, "Clinker_Fe2O3": clinker_fe2o3,
            "LSF": lsf, "SM": sm, "AM": am,
            "Kiln_Temp_C": kiln_temp, "Feed_Rate_tph": feed_rate, "Fan_Speed_rpm": fan_speed,
            "Sec_Air_Temp_C": sec_air_temp, "Fineness_90um_pct": fineness_90um
        }
        df_input = pd.DataFrame([row_dict])[feature_names]
        predicted_val = float(model.predict(df_input)[0])
        predicted_val = float(np.clip(predicted_val, 0.2, 5.0))

        # Top feature drivers from feature importances
        importances = model.feature_importances_
        sorted_indices = np.argsort(importances)[::-1]
        drivers = [
            {"feature": feature_names[idx], "importance": round(float(importances[idx]), 4), "value": round(float(df_input.iloc[0][feature_names[idx]]), 3)}
            for idx in sorted_indices[:5]
        ]
        source = "XGBoost Trained Model"
    else:
        # Physics heuristic fallback
        raw_pred = 0.80 + 3.2 * max(0.0, lsf - 0.94) + 0.08 * (fineness_90um - 12.0) - 0.006 * (kiln_temp - 1400)
        predicted_val = float(np.clip(raw_pred, 0.2, 5.0))
        drivers = [
            {"feature": "LSF", "importance": 0.45, "value": round(lsf, 4)},
            {"feature": "Kiln_Temp_C", "importance": 0.30, "value": round(kiln_temp, 1)},
            {"feature": "Fineness_90um_pct", "importance": 0.15, "value": round(fineness_90um, 2)},
        ]
        source = "Domain Chemistry Heuristic"

    return {
        "target": "Free CaO",
        "unit": "%",
        "prediction": round(predicted_val, 3),
        "confidence": round(confidence, 3),
        "source": source,
        "drivers": drivers,
        "ood_warnings": ood_warnings,
        "lsf": round(lsf, 4),
        "sm": round(sm, 4),
        "am": round(am, 4),
    }

def summarize_prediction(result: Dict[str, Any]) -> str:
    """Return a human-readable engineering summary of the prediction."""
    text = (
        f"Predicted {result['target']} = {result['prediction']} {result['unit']} "
        f"(Confidence: {result['confidence'] * 100:.1f}%, Engine: {result['source']})."
    )
    if result.get("ood_warnings"):
        text += " WARNINGS: " + " | ".join(result["ood_warnings"])
    return text
