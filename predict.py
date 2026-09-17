"""Prediction CLI for the AI Cement Engineer assistant.

This CLI accepts a JSON or CSV/Excel input containing feature values and outputs a
structured engineering result. It intentionally blocks unsupported clinker targets
unless a qualified measured target dataset is available.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable

import pandas as pd

from src.ml.prediction_service import PredictionService


def _safe_features_from_row(row: dict[str, Any]) -> dict[str, float]:
    return {str(k): float(v) for k, v in row.items() if v is not None}


def _load_features_from_path(path: str | Path) -> dict[str, float]:
    dataset = Path(path)
    if dataset.suffix.lower() == ".json":
        data = json.loads(dataset.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return _safe_features_from_row(data[0])
        if isinstance(data, dict):
            if "features" in data and isinstance(data["features"], dict):
                return {str(k): float(v) for k, v in data["features"].items()}
            return _safe_features_from_row(data)

    frame = pd.read_csv(dataset) if dataset.suffix.lower() == ".csv" else pd.read_excel(dataset)
    if frame.empty:
        raise ValueError(f"Input file {dataset} is empty.")
    return _safe_features_from_row(frame.iloc[0].to_dict())


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a structured AI engineering prediction for the supported repository targets.")
    parser.add_argument("--target", default="Free CaO", help="Target to predict, e.g. Free CaO or compressive_strength.")
    parser.add_argument("--input", type=str, help="JSON, CSV, or Excel file containing a single sample of engineering inputs.")
    parser.add_argument("--synthetic-demo", action="store_true", help="Allow synthetic demonstration output only for software testing.")
    args = parser.parse_args()

    if not args.input:
        raise SystemExit("--input is required and must point to a JSON, CSV, or Excel file.")

    features = _load_features_from_path(args.input)
    result = PredictionService().predict(features, args.target, synthetic_demo=args.synthetic_demo)
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
