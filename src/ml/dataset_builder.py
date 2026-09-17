"""Dataset builders and repository discovery helpers for the AI Cement Engineer."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import pandas as pd

from src.ml.data_catalog import build_data_catalog


def discover_datasets(repo_root: str | Path | None = None) -> List[Dict[str, Any]]:
    return build_data_catalog(repo_root=repo_root)["datasets"]


def load_dataset(path: str | Path) -> pd.DataFrame:
    dataset_path = Path(path)
    if dataset_path.suffix.lower() == ".csv":
        return pd.read_csv(dataset_path)
    if dataset_path.suffix.lower() in {".xls", ".xlsx"}:
        xls = pd.ExcelFile(dataset_path)
        if len(xls.sheet_names) == 1:
            return xls.parse(xls.sheet_names[0])
        return xls.parse(xls.sheet_names[0])
    if dataset_path.suffix.lower() == ".json":
        return pd.read_json(dataset_path)
    raise ValueError(f"Unsupported dataset format for {dataset_path}")


def choose_primary_dataset(repo_root: str | Path | None = None, *, prefer: Sequence[str] = ()) -> Dict[str, Any] | None:
    catalog = discover_datasets(repo_root)
    if prefer:
        lowered = {name.lower() for name in prefer}
        for item in catalog:
            if str(item.get("filename", "")).lower() in lowered or str(item.get("dataset_type", "")).lower() in lowered:
                return item
    for item in catalog:
        if item.get("dataset_type") == "REFERENCE/ASSAY":
            return item
    for item in catalog:
        if item.get("dataset_type") == "CONCRETE BENCHMARK":
            return item
    return catalog[0] if catalog else None
