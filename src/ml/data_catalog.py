"""Repository-wide dataset catalog and provenance classification.

This module inspects the repository's on-disk datasets and records their type,
shape, feature columns, target columns, missingness, duplicates, and provenance.
The classification is intentionally conservative: synthetic and derived columns are
never promoted to measured-clinker ground truth.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import pandas as pd


FILE_EXTENSIONS = {".csv", ".xls", ".xlsx", ".json"}


@dataclass
class DatasetEntry:
    filename: str
    path: str
    sheet_name: str = "Sheet1"
    dataset_type: str = "UNKNOWN"
    rows: int = 0
    columns: int = 0
    feature_columns: List[str] = field(default_factory=list)
    target_columns: List[str] = field(default_factory=list)
    units: Dict[str, str] = field(default_factory=dict)
    missing_values: Dict[str, int] = field(default_factory=dict)
    duplicate_rows: int = 0
    categorical_variables: List[str] = field(default_factory=list)
    timestamps: List[str] = field(default_factory=list)
    ids: List[str] = field(default_factory=list)
    provenance: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _dataset_kind(path: Path) -> str:
    lower = str(path).lower()
    parts = {p.lower() for p in path.parts}

    if "raw_materials" in parts or "raw_material" in parts:
        return "REFERENCE/ASSAY"
    if "raw_mix" in parts or "raw_mix" in lower:
        return "DERIVED/SYNTHETIC"
    if "concrete" in parts or "concrete" in lower:
        return "CONCRETE BENCHMARK"
    if "clinker" in parts or "clinker" in lower:
        return "CLINKER DATA"
    if "kiln" in parts or "kiln" in lower:
        return "PROCESS/TELEMETRY"
    if "cement" in parts or "cement" in lower:
        return "CEMENT QUALITY"
    if "synthetic" in lower or "demo" in lower:
        return "SYNTHETIC DEMONSTRATION"
    return "UNKNOWN"


def _is_id_column(name: str) -> bool:
    key = name.lower()
    return any(token in key for token in ["id", "sample", "batch", "date", "timestamp"]) and "target" not in key


def _target_like(name: str) -> bool:
    key = name.lower()
    target_tokens = [
        "strength",
        "compressive",
        "free",
        "cao",
        "c3s",
        "c2s",
        "c3a",
        "c4af",
        "blaine",
        "soundness",
        "setting",
        "loss",
        "so3",
        "fineness",
        "air",
        "slump",
    ]
    return any(token in key for token in target_tokens)


def _infer_units(columns: Sequence[str]) -> Dict[str, str]:
    unit_map: Dict[str, str] = {}
    for col in columns:
        lower = col.lower()
        if any(token in lower for token in ["cao", "sio2", "al2o3", "fe2o3", "mgo", "so3", "loi"]):
            unit_map[col] = "%"
        elif "temp" in lower or "temperature" in lower:
            unit_map[col] = "°C"
        elif "rate" in lower or "feed" in lower:
            unit_map[col] = "tph or kg/m3"
        elif "day" in lower or "age" in lower:
            unit_map[col] = "day"
        elif "strength" in lower:
            unit_map[col] = "MPa"
        elif "blaine" in lower:
            unit_map[col] = "m2/kg"
        elif "fineness" in lower:
            unit_map[col] = "m2/kg"
        elif "pressure" in lower:
            unit_map[col] = "kPa"
        elif "speed" in lower:
            unit_map[col] = "rpm"
        elif "moisture" in lower:
            unit_map[col] = "%"
    return unit_map


def _summarize_dataframe(df: pd.DataFrame, *, path: Path, sheet_name: str, dataset_type: str) -> DatasetEntry:
    columns = list(df.columns)
    feature_columns = [col for col in columns if not _target_like(col) and not _is_id_column(col)]
    target_columns = [col for col in columns if _target_like(col)]
    missing_values = {str(col): int(df[col].isna().sum()) for col in columns if df[col].isna().sum() > 0}
    categorical_variables = [str(col) for col in columns if df[col].dtype == "object"]
    timestamps = [str(col) for col in columns if any(token in str(col).lower() for token in ["date", "time", "timestamp"]) ]
    ids = [str(col) for col in columns if _is_id_column(col)]
    duplicate_rows = int(df.duplicated().sum())

    provenance = "Measured or repository-provided source; classify carefully before using as a training target."
    if dataset_type in {"REFERENCE/ASSAY", "CONCRETE BENCHMARK"}:
        provenance = "Repository source with assay or benchmark provenance; do not conflate with measured clinker targets."
    elif dataset_type.startswith("DERIVED") or "synthetic" in dataset_type.lower():
        provenance = "Derived or synthetic demonstration data; not valid measured clinker ground truth."
    elif dataset_type == "CLINKER DATA":
        provenance = "Clinker data require measured sample-level provenance before use as supervised training labels."
    elif dataset_type == "UNKNOWN":
        provenance = "Unclassified repository asset; classification pending validation."

    notes = "Synthetic or Bogue-derived outputs are not treated as real measured clinker labels."
    if dataset_type == "REFERENCE/ASSAY":
        notes = "Assay/reference data are valid for raw-material chemistry and engineering feature generation, not for real clinker ML labels."
    if dataset_type == "CONCRETE BENCHMARK":
        notes = "Concrete benchmark data are valid only for downstream concrete-strength benchmarking and not for clinker-phase prediction."

    return DatasetEntry(
        filename=path.name,
        path=str(path),
        sheet_name=sheet_name,
        dataset_type=dataset_type,
        rows=int(df.shape[0]),
        columns=int(df.shape[1]),
        feature_columns=feature_columns,
        target_columns=target_columns,
        units=_infer_units(columns),
        missing_values=missing_values,
        duplicate_rows=duplicate_rows,
        categorical_variables=categorical_variables,
        timestamps=timestamps,
        ids=ids,
        provenance=provenance,
        notes=notes,
    )


def _read_dataframe(path: Path) -> Iterable[pd.DataFrame]:
    if path.suffix.lower() == ".csv":
        yield pd.read_csv(path)
        return

    if path.suffix.lower() in {".xls", ".xlsx"}:
        xls = pd.ExcelFile(path)
        for sheet_name in xls.sheet_names:
            yield xls.parse(sheet_name)
        return

    if path.suffix.lower() == ".json":
        data = pd.read_json(path)
        yield data
        return

    raise ValueError(f"Unsupported dataset format for {path}")


def discover_repository_datasets(repo_root: str | Path | None = None) -> List[DatasetEntry]:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[2]
    datasets: List[DatasetEntry] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in FILE_EXTENSIONS:
            continue
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        dataset_type = _dataset_kind(path)
        for sheet_name, frame in _sheet_iterator(path):
            datasets.append(_summarize_dataframe(frame, path=path, sheet_name=sheet_name, dataset_type=dataset_type))
    return datasets


def _sheet_iterator(path: Path):
    if path.suffix.lower() == ".csv":
        yield "Sheet1", pd.read_csv(path)
        return
    if path.suffix.lower() in {".xls", ".xlsx"}:
        xls = pd.ExcelFile(path)
        for sheet_name in xls.sheet_names:
            yield sheet_name, xls.parse(sheet_name)
        return
    if path.suffix.lower() == ".json":
        try:
            data = pd.read_json(path)
        except Exception:
            return
        if isinstance(data, pd.DataFrame):
            yield "Sheet1", data
            return
        if isinstance(data, dict):
            yield "Sheet1", pd.DataFrame(data)


def build_data_catalog(repo_root: str | Path | None = None) -> Dict[str, Any]:
    datasets = discover_repository_datasets(repo_root=repo_root)
    summary = {
        "total_datasets": len(datasets),
        "reference_assay": sum(1 for item in datasets if item.dataset_type == "REFERENCE/ASSAY"),
        "synthetic_demo": sum(1 for item in datasets if "synthetic" in item.dataset_type.lower() or "derived" in item.dataset_type.lower()),
        "concrete_benchmark": sum(1 for item in datasets if item.dataset_type == "CONCRETE BENCHMARK"),
        "measured_clinker": sum(1 for item in datasets if item.dataset_type == "CLINKER DATA"),
        "blocked_targets": ["Free CaO", "C3S", "C2S", "C3A", "C4AF"],
    }
    return {"datasets": [entry.to_dict() for entry in datasets], "summary": summary}
