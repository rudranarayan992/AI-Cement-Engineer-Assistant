"""Cement compressive strength prediction module (3-day, 7-day, 28-day)."""

from __future__ import annotations

import os
import joblib
import pandas as pd
import numpy as np
from typing import Any, Dict

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "models",
    "strength_28d_xgb.joblib"
)

_cached_strength_model = None

def _get_model():
    global _cached_strength_model
    if _cached_strength_model is None and os.path.exists(MODEL_PATH):
        try:
            _cached_strength_model = joblib.load(MODEL_PATH)
        except Exception:
            _cached_strength_model = False
    return _cached_strength_model

def predict_compressive_strength(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Predict 3d, 7d, and 28d compressive strength in MPa from clinker phases and cement parameters.

    Inputs:
    - C3S_pct (50.0 - 70.0)
    - C2S_pct (10.0 - 25.0)
    - C3A_pct (4.0 - 12.0)
    - C4AF_pct (6.0 - 14.0)
    - Free_CaO_pct (0.5 - 3.0)
    - Blaine_cm2g (3000 - 4500)
    - Gypsum_SO3_pct (2.0 - 3.5)
    - WC_Ratio (0.40 - 0.55)
    """
    c3s = float(inputs.get("C3S_pct", 58.5))
    c2s = float(inputs.get("C2S_pct", 16.2))
    c3a = float(inputs.get("C3A_pct", 7.8))
    c4af = float(inputs.get("C4AF_pct", 9.4))
    free_cao = float(inputs.get("Free_CaO_pct", 1.2))
    blaine = float(inputs.get("Blaine_cm2g", 3600.0))
    gypsum = float(inputs.get("Gypsum_SO3_pct", 2.8))
    wc = float(inputs.get("WC_Ratio", 0.48))

    model_data = _get_model()

    if model_data and isinstance(model_data, dict):
        model = model_data["model"]
        feature_names = model_data["features"]
        df_in = pd.DataFrame([{
            "C3S_pct": c3s, "C2S_pct": c2s, "C3A_pct": c3a, "C4AF_pct": c4af,
            "Free_CaO_pct": free_cao, "Blaine_cm2g": blaine, "Gypsum_SO3_pct": gypsum, "WC_Ratio": wc
        }])[feature_names]
        str_28d = float(model.predict(df_in)[0])
    else:
        str_28d = 32.0 + 0.52 * c3s + 0.48 * c2s + 0.20 * c3a + 0.0055 * (blaine - 3000) - 48.0 * (wc - 0.45) - 2.2 * free_cao

    # Standard maturity curve scaling for 3d and 7d strength
    str_3d = max(10.0, str_28d * (0.45 + 0.003 * (c3a - 7.0)))
    str_7d = max(18.0, str_28d * (0.72 + 0.002 * (c3s - 55.0)))
    str_28d = max(25.0, str_28d)

    # ASTM C150 Quality Grade Classification
    if str_28d >= 52.5:
        grade = "Type I/II High Early / 52.5N Grade (Premium Strength)"
    elif str_28d >= 42.5:
        grade = "Type I Standard Portland / 42.5N Grade (Standard)"
    else:
        grade = "Type IV Low Heat / 32.5N Grade (Moderate Strength)"

    return {
        "strength_3d_MPa": round(str_3d, 2),
        "strength_7d_MPa": round(str_7d, 2),
        "strength_28d_MPa": round(str_28d, 2),
        "grade_classification": grade,
        "blaine": blaine,
        "wc_ratio": wc,
        "c3s": c3s,
        "c3a": c3a,
    }
