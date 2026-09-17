"""Lightweight helpers for recording actual lab results and interfacing with CaseRegistry."""
from __future__ import annotations

from typing import Optional

from src.ml.case_registry import CaseRegistry


class ActualTracker:
    def __init__(self, db_path: str | None = None):
        self.registry = CaseRegistry(db_path=db_path or "cases.db")

    def record_actual_result(self, case_id: str, actual_value: float, measurement_source: str, measurement_method: str, measurement_date: str | None = None, measurement_uncertainty: float | None = None, notes: str = "") -> None:
        self.registry.record_actual(
            case_id=case_id,
            actual_value=actual_value,
            measurement_source=measurement_source,
            measurement_method=measurement_method,
            measurement_date=measurement_date,
            measurement_uncertainty=measurement_uncertainty,
            notes=notes,
        )

    def get_error_stats(self, target: str):
        return self.registry.get_error_statistics(target)
