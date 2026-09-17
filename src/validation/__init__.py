"""Validation layer for physics and chemistry constraints.

Provides orchestration of chemistry, moduli, and phase validation
with configurable operational limits.
"""

from .clinker_data_acceptance import validate_clinker_dataset, validate_clinker_record

__version__ = "0.1.0"
__all__ = ["validate_clinker_dataset", "validate_clinker_record"]
