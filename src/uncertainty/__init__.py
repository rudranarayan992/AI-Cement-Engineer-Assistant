"""Uncertainty and out-of-distribution monitoring for model wrappers.

This package is intentionally separate from model training and validation logic.
It provides reusable feature-space diagnostics that can wrap both baseline ML
and PIML models without entangling them with engineering constraints.
"""

from .ood import OODConfig, FeatureOODMonitor, PredictionUncertaintyWrapper

__all__ = [
    "OODConfig",
    "FeatureOODMonitor",
    "PredictionUncertaintyWrapper",
]
