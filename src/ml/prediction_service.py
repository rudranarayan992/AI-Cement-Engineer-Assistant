"""Prediction service for the AI Cement Engineer assistant.

This service exposes a clean target-aware API for clinker-quality prediction for
Free CaO, C3S, C2S, C3A, and C4AF while enforcing the repository's scientific
safety rule: no real clinker prediction is allowed without measured clinker data.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

from src.explainability.engineering_interpreter import interpret_prediction
from src.explainability.shap_service import compute_shap_response
from src.ml.model_registry import get_model_registry
from src.ml.preprocessing import prepare_feature_vector
from src.ml.target_schema import REQUIRED_TARGETS, build_prediction_schema, normalize_target_name
from src.uncertainty.ood import FeatureOODMonitor, OODConfig
from src.validation.physics_constraints import validate_all


class PredictionService:
    """Target-aware prediction service wrapping the existing conservative validation stack."""

    def __init__(self) -> None:
        self.registry = get_model_registry()
        self.ood_monitor = FeatureOODMonitor(
            feature_names=["LSF", "SM", "AM", "Kiln_Temp_C", "Feed_Rate_tph"],
            config=OODConfig(z_score_threshold=3.0, mahalanobis_threshold=3.0),
        )

    def predict(self, features: Mapping[str, Any], target: str, *, synthetic_demo: bool = False) -> Dict[str, Any]:
        target_name = normalize_target_name(target)
        if target_name not in REQUIRED_TARGETS:
            raise ValueError(f"Unsupported target '{target}'. Supported targets: {sorted(REQUIRED_TARGETS)}")

        feature_dict = prepare_feature_vector(features)
        model_meta = self.registry.get(target_name)
        if model_meta is None or model_meta.deployment_status == "RESEARCH_DATA_BLOCKED":
            block_message = (
                "Qualified measured clinker labels with traceable sample/process/laboratory provenance are required for real clinker ML."
            )
            return build_prediction_schema(
                prediction=None,
                target=target_name,
                unit=REQUIRED_TARGETS[target_name]["unit"],
                model_version="research-blocked",
                confidence=0.0,
                uncertainty=1.0,
                ood_status="RESEARCH DATA BLOCKED",
                physics_status="RESEARCH DATA BLOCKED",
                warnings=[block_message],
                provenance={
                    "data_status": "RESEARCH DATA BLOCKED",
                    "training_data_type": "RESEARCH_DATA_BLOCKED",
                    "dataset_status": "No qualified measured clinker dataset available",
                    "synthetic_demo_allowed": bool(synthetic_demo),
                },
            )

        if synthetic_demo:
            demo_prediction = 1.0
            if target_name == "C3S":
                demo_prediction = 60.0
            elif target_name == "C2S":
                demo_prediction = 18.0
            elif target_name == "C3A":
                demo_prediction = 8.5
            elif target_name == "C4AF":
                demo_prediction = 10.5
            elif target_name == "Free CaO":
                demo_prediction = 1.2

            ood_status = "SYNTHETIC DEMO"
            physics_status = "OK"
            warnings = ["Synthetic demo only. This output is not measured industrial ground truth. Use only for software demonstration or testing."]
            drivers = compute_shap_response(feature_dict, target_name)
            interpretation = interpret_prediction(target_name, demo_prediction, drivers.get("top_drivers", []), ood_status, physics_status)
            return build_prediction_schema(
                prediction=demo_prediction,
                target=target_name,
                unit=REQUIRED_TARGETS[target_name]["unit"],
                model_version=model_meta.version,
                confidence=0.4,
                uncertainty=0.6,
                ood_status=ood_status,
                physics_status=physics_status,
                warnings=warnings,
                provenance={
                    "data_status": "SYNTHETIC DEMO",
                    "training_data_type": "SYNTHETIC",
                    "dataset_status": "Synthetic demo only; not valid measured clinker ground truth",
                    "synthetic_demo_allowed": True,
                },
            ) | {
                "explanation": interpretation,
                "drivers": drivers,
            }

        # Default to blocked state until measured data exist.
        block_message = (
            "Qualified measured clinker labels with traceable sample/process/laboratory provenance are required for real clinker ML."
        )
        return build_prediction_schema(
            prediction=None,
            target=target_name,
            unit=REQUIRED_TARGETS[target_name]["unit"],
            model_version=model_meta.version,
            confidence=0.0,
            uncertainty=1.0,
            ood_status="RESEARCH DATA BLOCKED",
            physics_status="RESEARCH DATA BLOCKED",
            warnings=[block_message],
            provenance={
                "data_status": "RESEARCH DATA BLOCKED",
                "training_data_type": model_meta.training_data_type,
                "dataset_status": "No qualified measured clinker dataset available",
                "synthetic_demo_allowed": False,
            },
        )

    def explain(self, features: Mapping[str, Any], target: str) -> Dict[str, Any]:
        target_name = normalize_target_name(target)
        shap = compute_shap_response(features, target_name)
        return {
            "target": target_name,
            "status": shap.get("status", "RESEARCH DATA BLOCKED"),
            "top_drivers": shap.get("top_drivers", []),
            "model_association_note": shap.get("model_association_note", "Model association only; not causation."),
            "causal_note": shap.get("causal_note", "Causal mechanism requires measured process, chemistry, and lab evidence."),
        }


def predict_target(features: Mapping[str, Any], target: str, *, synthetic_demo: bool = False) -> Dict[str, Any]:
    return PredictionService().predict(features, target, synthetic_demo=synthetic_demo)


def explain_target(features: Mapping[str, Any], target: str) -> Dict[str, Any]:
    return PredictionService().explain(features, target)
