"""Unified target engine for prediction gating and metadata.

Provides a thin layer over the existing TARGET_REGISTRY and PredictionService
that centralizes checks, provenance, and blocked-target messaging.
"""
from __future__ import annotations

from typing import Any, Dict

from src.ml.target_registry import TARGET_REGISTRY, get_target_entry
from src.ml.prediction_service import PredictionService
from src.ml.case_registry import CaseRegistry


class TargetEngine:
    """High-level API for requesting predictions while enforcing scientific gates."""

    def __init__(self, case_db_path: str | None = None):
        self.pred_service = PredictionService()
        self.case_registry = CaseRegistry(db_path=case_db_path or "cases.db")

    def request_prediction(self, features: Dict[str, Any], target: str, *, synthetic_demo: bool = False) -> Dict[str, Any]:
        target_entry = get_target_entry(target)
        # Enforce registry status
        if target_entry.get("status") == "BLOCKED" and not synthetic_demo:
            # Build blocked response via PredictionService to keep consistent schema
            resp = self.pred_service.predict(features, target, synthetic_demo=False)
            # Record case as blocked with provenance
            case_id = self.case_registry.record_case(
                target=resp["target"],
                unit=resp["unit"],
                input_dict=features,
                prediction=None,
                confidence=0.0,
                uncertainty=1.0,
                ood_status=resp.get("ood_status", "RESEARCH DATA BLOCKED"),
                physics_status=resp.get("physics_status", "RESEARCH DATA BLOCKED"),
                warnings=resp.get("warnings", []),
                provenance="RESEARCH_DATA_BLOCKED",
                explanation=resp.get("explanation"),
                drivers=resp.get("drivers"),
                features_normalized=None,
            )
            resp["case_id"] = case_id
            return resp
        # Otherwise forward to prediction service
        resp = self.pred_service.predict(features, target, synthetic_demo=synthetic_demo)
        # persist case
        case_id = self.case_registry.record_case(
            target=resp["target"],
            unit=resp["unit"],
            input_dict=features,
            prediction=resp.get("prediction"),
            confidence=resp.get("confidence", 0.0),
            uncertainty=resp.get("uncertainty", 1.0),
            ood_status=resp.get("ood_status", "UNKNOWN"),
            physics_status=resp.get("physics_status", "UNKNOWN"),
            warnings=resp.get("warnings", []),
            provenance=resp.get("provenance", {}).get("data_status", "PREDICTED"),
            explanation=resp.get("explanation"),
            drivers=resp.get("drivers"),
            features_normalized=None,
        )
        resp["case_id"] = case_id
        return resp
