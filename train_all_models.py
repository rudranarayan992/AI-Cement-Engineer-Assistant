#!/usr/bin/env python3
"""Repository training entrypoint for the AI Cement Engineer pipeline.

This script discovers datasets, classifies them, and trains any targets that are
actually supported by measured data in the repository. Clinker-quality targets with
no qualified measured labels are skipped safely and recorded as blocked.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from src.ml.data_catalog import build_data_catalog
from src.ml.model_training import train_all_eligible_targets


def main() -> None:
    repo_root = Path(__file__).resolve().parent
    catalog = build_data_catalog(repo_root)
    training_results = train_all_eligible_targets(repo_root)

    print(json.dumps({
        "catalog_summary": catalog["summary"],
        "training_results": training_results,
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
