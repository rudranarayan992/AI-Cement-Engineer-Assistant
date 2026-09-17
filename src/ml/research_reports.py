"""Tiny research reporting helper to export simple model/case summaries.

Generates CSV/JSON summaries suitable for inclusion in reports.
"""
from __future__ import annotations

import json
from typing import Dict, Any

import pandas as pd
from src.ml.case_registry import CaseRegistry


class ResearchReporter:
    def __init__(self, db_path: str | None = None):
        self.registry = CaseRegistry(db_path=db_path or "cases.db")

    def export_case_summary(self, target: str, out_csv: str | None = None) -> pd.DataFrame:
        df = self.registry.export_cases_dataframe(target=target)
        if out_csv:
            df.to_csv(out_csv, index=False)
        return df

    def export_json(self, target: str, out_path: str):
        df = self.export_case_summary(target)
        payload = df.to_dict(orient="records")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return out_path
