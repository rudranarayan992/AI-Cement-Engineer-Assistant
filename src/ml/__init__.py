"""Machine-learning package for the AI Cement Engineer assistant."""

from .case_registry import CaseRegistry, CaseMetadata, CaseActual, CaseError
from .data_catalog import DatasetEntry, build_data_catalog, discover_repository_datasets
from .dataset_builder import choose_primary_dataset, discover_datasets, load_dataset
from .evaluation import compute_regression_metrics, summarize_predictions
from .feature_engineering import apply_missing_value_policy, build_ml_feature_matrix, normalize_feature_names, safe_numeric_conversion
from .model_metadata import ModelMetadata
from .model_registry import get_model_metadata, get_model_registry
from .model_training import train_all_eligible_targets
from .prediction_service import PredictionService, explain_target, predict_target
from .target_registry import TARGET_REGISTRY, get_registered_targets, get_target_entry
from .unified_input import UnifiedInputParser, NormalizedInput, MaterialComposition

__all__ = [
    "CaseRegistry",
    "CaseMetadata",
    "CaseActual",
    "CaseError",
    "DatasetEntry",
    "build_data_catalog",
    "discover_repository_datasets",
    "choose_primary_dataset",
    "discover_datasets",
    "load_dataset",
    "normalize_feature_names",
    "safe_numeric_conversion",
    "apply_missing_value_policy",
    "build_ml_feature_matrix",
    "compute_regression_metrics",
    "summarize_predictions",
    "ModelMetadata",
    "get_model_metadata",
    "get_model_registry",
    "train_all_eligible_targets",
    "PredictionService",
    "predict_target",
    "explain_target",
    "TARGET_REGISTRY",
    "get_registered_targets",
    "get_target_entry",
    "UnifiedInputParser",
    "NormalizedInput",
    "MaterialComposition",
]
