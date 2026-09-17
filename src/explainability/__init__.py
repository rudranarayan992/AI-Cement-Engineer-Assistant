"""Model explainability and engineering insights."""

from .xai import feature_importance_summary, shap_summary
from .strength_explainer import StrengthExplainer, compare_cement_batches
from .engineering_interpreter import interpret_prediction
from .shap_service import compute_shap_response, get_top_drivers

__all__ = [
    "feature_importance_summary",
    "shap_summary",
    "StrengthExplainer",
    "compare_cement_batches",
    "compute_shap_response",
    "get_top_drivers",
    "interpret_prediction",
]
