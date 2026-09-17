"""Metadata definitions for target-specific model registry entries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ModelMetadata:
    target: str
    model_type: str
    version: str
    training_data_type: str
    sample_count: int
    features: List[str] = field(default_factory=list)
    validation_method: str = "temporal_holdout"
    temporal_validation_status: str = "NOT_AVAILABLE"
    leakage_status: str = "UNKNOWN"
    uncertainty_method: str = "feature_ood_monitor"
    ood_method: str = "mahalanobis_zscore"
    physics_validation: str = "enabled"
    deployment_status: str = "RESEARCH_DATA_BLOCKED"
    notes: str = "Qualified measured clinker labels are required before real industrial deployment."

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target": self.target,
            "model_type": self.model_type,
            "version": self.version,
            "training_data_type": self.training_data_type,
            "number_of_samples": self.sample_count,
            "features": self.features,
            "validation_method": self.validation_method,
            "temporal_validation_status": self.temporal_validation_status,
            "leakage_status": self.leakage_status,
            "uncertainty_method": self.uncertainty_method,
            "ood_method": self.ood_method,
            "physics_validation": self.physics_validation,
            "deployment_status": self.deployment_status,
            "notes": self.notes,
        }
