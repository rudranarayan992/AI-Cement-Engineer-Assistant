"""Model registry for supported clinker-quality research targets.

This registry is intentionally conservative: no real clinker model is marked as
available unless a qualified measured clinker dataset exists with sample-level
provenance.
"""

from __future__ import annotations

from typing import Dict, List

from src.ml.model_metadata import ModelMetadata


def create_default_registry() -> Dict[str, ModelMetadata]:
    return {
        "Free CaO": ModelMetadata(
            target="Free CaO",
            model_type="CLINKER_QUALITY_REGRESSION",
            version="research-blocked",
            training_data_type="RESEARCH_DATA_BLOCKED",
            sample_count=0,
            features=["CaO", "SiO2", "Al2O3", "Fe2O3", "LSF", "Kiln_Temp_C"],
            validation_method="not_available",
            temporal_validation_status="NOT_AVAILABLE",
            leakage_status="UNVERIFIED",
            uncertainty_method="feature_ood_monitor",
            ood_method="mahalanobis_zscore",
            physics_validation="enabled",
            deployment_status="RESEARCH_DATA_BLOCKED",
            notes="Qualified measured clinker labels with traceable sample/process/laboratory provenance are required for real clinker ML.",
        ),
        "C3S": ModelMetadata(
            target="C3S",
            model_type="CLINKER_PHASE_REGRESSION",
            version="research-blocked",
            training_data_type="RESEARCH_DATA_BLOCKED",
            sample_count=0,
            features=["CaO", "SiO2", "Al2O3", "Fe2O3", "LSF", "SM", "AM"],
            validation_method="not_available",
            temporal_validation_status="NOT_AVAILABLE",
            leakage_status="UNVERIFIED",
            uncertainty_method="feature_ood_monitor",
            ood_method="mahalanobis_zscore",
            physics_validation="enabled",
            deployment_status="RESEARCH_DATA_BLOCKED",
            notes="Qualified measured clinker labels with traceable sample/process/laboratory provenance are required for real clinker ML.",
        ),
        "C2S": ModelMetadata(
            target="C2S",
            model_type="CLINKER_PHASE_REGRESSION",
            version="research-blocked",
            training_data_type="RESEARCH_DATA_BLOCKED",
            sample_count=0,
            features=["CaO", "SiO2", "Al2O3", "Fe2O3", "LSF", "SM", "AM"],
            validation_method="not_available",
            temporal_validation_status="NOT_AVAILABLE",
            leakage_status="UNVERIFIED",
            uncertainty_method="feature_ood_monitor",
            ood_method="mahalanobis_zscore",
            physics_validation="enabled",
            deployment_status="RESEARCH_DATA_BLOCKED",
            notes="Qualified measured clinker labels with traceable sample/process/laboratory provenance are required for real clinker ML.",
        ),
        "C3A": ModelMetadata(
            target="C3A",
            model_type="CLINKER_PHASE_REGRESSION",
            version="research-blocked",
            training_data_type="RESEARCH_DATA_BLOCKED",
            sample_count=0,
            features=["Al2O3", "Fe2O3", "AM", "LSF"],
            validation_method="not_available",
            temporal_validation_status="NOT_AVAILABLE",
            leakage_status="UNVERIFIED",
            uncertainty_method="feature_ood_monitor",
            ood_method="mahalanobis_zscore",
            physics_validation="enabled",
            deployment_status="RESEARCH_DATA_BLOCKED",
            notes="Qualified measured clinker labels with traceable sample/process/laboratory provenance are required for real clinker ML.",
        ),
        "C4AF": ModelMetadata(
            target="C4AF",
            model_type="CLINKER_PHASE_REGRESSION",
            version="research-blocked",
            training_data_type="RESEARCH_DATA_BLOCKED",
            sample_count=0,
            features=["Fe2O3", "Al2O3", "AM", "LSF"],
            validation_method="not_available",
            temporal_validation_status="NOT_AVAILABLE",
            leakage_status="UNVERIFIED",
            uncertainty_method="feature_ood_monitor",
            ood_method="mahalanobis_zscore",
            physics_validation="enabled",
            deployment_status="RESEARCH_DATA_BLOCKED",
            notes="Qualified measured clinker labels with traceable sample/process/laboratory provenance are required for real clinker ML.",
        ),
    }


MODEL_REGISTRY = create_default_registry()


def get_model_registry() -> Dict[str, ModelMetadata]:
    return MODEL_REGISTRY


def get_model_metadata(target: str) -> ModelMetadata:
    return MODEL_REGISTRY["Free CaO" if target.lower() == "free cao" else target]
