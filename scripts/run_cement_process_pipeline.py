"""Run the repository's deterministic cement analytics pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from src.pipeline.cement_process_pipeline import build_cement_process_pipeline


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    pipeline = build_cement_process_pipeline(project_root / "data")
    print(json.dumps(pipeline["summary"], indent=2, default=str))
