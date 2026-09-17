"""Tests for OOD and uncertainty utilities."""

import pandas as pd
import pytest

from src.uncertainty.ood import FeatureOODMonitor, OODConfig, PredictionUncertaintyWrapper


def test_monitor_fit_and_eval_in_distribution():
    df = pd.DataFrame(
        {
            "LSF": [0.98, 1.00, 0.99, 1.02],
            "SM": [2.4, 2.5, 2.3, 2.6],
            "AM": [1.7, 1.8, 1.6, 1.9],
        }
    )
    monitor = FeatureOODMonitor(config=OODConfig(z_score_threshold=3.0, mahalanobis_threshold=3.0))
    monitor.fit(df)

    result = monitor.evaluate({"LSF": 1.00, "SM": 2.5, "AM": 1.8})

    assert result["valid"] is True
    assert result["ood_flag"] is False
    assert result["confidence"] >= 0.8


def test_monitor_detects_ood_sample():
    df = pd.DataFrame(
        {
            "LSF": [0.98, 1.00, 0.99, 1.02],
            "SM": [2.4, 2.5, 2.3, 2.6],
            "AM": [1.7, 1.8, 1.6, 1.9],
        }
    )
    monitor = FeatureOODMonitor(config=OODConfig(z_score_threshold=2.5, mahalanobis_threshold=2.5))
    monitor.fit(df)

    result = monitor.evaluate({"LSF": 1.50, "SM": 1.0, "AM": 3.0})

    assert result["ood_flag"] is True
    assert len(result["warnings"]) > 0


def test_monitor_raises_for_missing_features():
    df = pd.DataFrame(
        {
            "LSF": [0.98, 1.00, 0.99],
            "SM": [2.4, 2.5, 2.3],
            "AM": [1.7, 1.8, 1.6],
        }
    )
    monitor = FeatureOODMonitor(feature_names=["LSF", "SM", "AM"])
    monitor.fit(df)

    with pytest.raises(ValueError):
        monitor.evaluate({"LSF": 1.0, "SM": 2.4})


def test_prediction_wrapper_tracks_confidence():
    df = pd.DataFrame(
        {
            "LSF": [0.98, 1.00, 0.99, 1.02],
            "SM": [2.4, 2.5, 2.3, 2.6],
            "AM": [1.7, 1.8, 1.6, 1.9],
        }
    )
    monitor = FeatureOODMonitor(config=OODConfig(z_score_threshold=3.0, mahalanobis_threshold=3.0))
    monitor.fit(df)
    wrapper = PredictionUncertaintyWrapper(monitor, model_name="toy_regressor")

    result = wrapper.assess({"LSF": 1.00, "SM": 2.5, "AM": 1.8}, prediction=1.15)

    assert result["prediction"] == 1.15
    assert result["valid"] is True
    assert result["confidence"] >= 0.8
    assert result["ood_flag"] is False


def test_prediction_wrapper_flags_ood_for_extreme_input():
    df = pd.DataFrame(
        {
            "LSF": [0.98, 1.00, 0.99, 1.02],
            "SM": [2.4, 2.5, 2.3, 2.6],
            "AM": [1.7, 1.8, 1.6, 1.9],
        }
    )
    monitor = FeatureOODMonitor(config=OODConfig(z_score_threshold=2.5, mahalanobis_threshold=2.5))
    monitor.fit(df)
    wrapper = PredictionUncertaintyWrapper(monitor, model_name="toy_regressor")

    result = wrapper.assess({"LSF": 1.4, "SM": 1.0, "AM": 3.2}, prediction=2.8)

    assert result["ood_flag"] is True
    assert result["confidence"] < 0.8
    assert len(result["warnings"]) > 0


def test_monitor_rejects_empty_reference_data():
    monitor = FeatureOODMonitor()
    with pytest.raises(ValueError):
        monitor.fit(pd.DataFrame({}))
