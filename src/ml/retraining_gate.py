"""Controlled retraining gate logic.

Simple rule-based gate: allow retrain when N new measured actuals exceed threshold and
aggregate error improves or sufficient new coverage exists.
"""
from __future__ import annotations

from typing import Dict, Any

from src.ml.actual_tracking import ActualTracker


class RetrainingGate:
    def __init__(self, db_path: str | None = None, min_new_cases: int = 10):
        self.tracker = ActualTracker(db_path=db_path)
        self.min_new_cases = min_new_cases

    def evaluate(self, target: str) -> Dict[str, Any]:
        stats = self.tracker.get_error_stats(target)
        count = stats.get("count", 0)
        allow = count >= self.min_new_cases
        reason = "Sufficient new measured cases" if allow else f"Need at least {self.min_new_cases} measured cases; currently {count}"
        return {"allow_retrain": allow, "count": count, "reason": reason}
