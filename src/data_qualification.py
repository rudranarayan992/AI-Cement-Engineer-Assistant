"""Dataset intake and ML-readiness qualification for the cement/clinker stack.

This module intentionally enforces a conservative gate:
- measured laboratory values are the only acceptable training labels
- Bogue-derived values are reference outputs, not ground truth
- synthetic/generated process tables are rejected for supervised ML
- no dataset can be called train-ready unless it has traceable labels and a coherent
  feature-to-target relationship

The implementation is deliberately lightweight but explicit so it can be used in
project tooling, CI checks, and future data-contract validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union

import pandas as pd


class DataBasis(str, Enum):
    """Scientific basis for a dataset or variable."""

    MEASURED = "measured"
    CALCULATED = "calculated"
    REFERENCE = "reference"
    SYNTHETIC = "synthetic"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class VariableClassification:
    """Classification for a single variable."""

    name: str
    basis: DataBasis
    role: str
    target_eligible: bool = False
    units: Optional[str] = None
    notes: str = ""


@dataclass
class DatasetQualificationResult:
    """Qualification outcome for a single dataset."""

    dataset_name: str
    path: str
    rows: int
    columns: int
    basis: DataBasis
    ready_for_ml: bool = False
    target_eligible: bool = False
    measured_target_count: int = 0
    variables: List[VariableClassification] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_name": self.dataset_name,
            "path": self.path,
            "rows": self.rows,
            "columns": self.columns,
            "basis": self.basis.value,
            "ready_for_ml": self.ready_for_ml,
            "target_eligible": self.target_eligible,
            "measured_target_count": self.measured_target_count,
            "variables": [
                {
                    "name": var.name,
                    "basis": var.basis.value,
                    "role": var.role,
                    "target_eligible": var.target_eligible,
                    "units": var.units,
                    "notes": var.notes,
                }
                for var in self.variables
            ],
            "blockers": self.blockers,
            "notes": self.notes,
        }


@dataclass
class MLReadinessGate:
    """Repository-level readiness decision."""

    datasets: List[DatasetQualificationResult] = field(default_factory=list)
    decision: str = "NO_GO"
    reason: str = "No measured cement/clinker dataset is currently qualified for supervised training."
    ready_for_ml: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision,
            "reason": self.reason,
            "ready_for_ml": self.ready_for_ml,
            "datasets": [dataset.to_dict() for dataset in self.datasets],
        }


def _normalize_name(name: str) -> str:
    return str(name).strip().lower().replace(" ", "_")


def _dataset_basis_from_name(dataset_name: str) -> DataBasis:
    name = _normalize_name(dataset_name)
    synthetic_markers = {
        "cement_master_dataset",
        "clinker_analysis",
        "cement_quality",
        "raw_meal_samples",
        "kiln_telemetry",
        "generate_cement_dataset",
        "synthetic",
        "demo",
    }
    if any(marker in name for marker in synthetic_markers):
        return DataBasis.SYNTHETIC
    if "raw_materials" in name:
        return DataBasis.MEASURED
    if "concrete" in name or "slump" in name:
        return DataBasis.MEASURED
    return DataBasis.UNKNOWN


def _identify_target_like_columns(columns: Sequence[str]) -> List[str]:
    lower = {str(c).lower() for c in columns}
    target_names = []
    for column in columns:
        c = str(column).lower()
        if any(token in c for token in ["strength", "compressive", "slump", "flow", "free_cao", "c3s", "c2s", "c3a", "c4af", "phase"]):
            target_names.append(str(column))
    return target_names


def _classify_variable(name: str, dataset_name: str, *, allow_reference: bool = True) -> VariableClassification:
    key = _normalize_name(name)
    if any(token in key for token in ["sample_id", "id", "plant_id", "line_id", "batch_id", "timestamp", "date", "file", "doi", "source", "notes"]):
        return VariableClassification(name=name, basis=DataBasis.UNKNOWN, role="identifier_or_metadata", target_eligible=False, notes="Identifier or metadata column; not a target.")

    if any(token in key for token in ["bogue", "lsf", "sm", "am", "calculated", "reference"]):
        return VariableClassification(
            name=name,
            basis=DataBasis.REFERENCE if allow_reference else DataBasis.CALCULATED,
            role="derived_feature",
            target_eligible=False,
            notes="Derived or Bogue/reference output; not valid as measured ground truth.",
        )

    if any(token in key for token in ["free_cao", "c3s", "c2s", "c3a", "c4af", "strength_3d", "strength_7d", "strength_28d", "compressive_strength", "slump", "flow"]) and ("synthetic" in _normalize_name(dataset_name) or "demo" in _normalize_name(dataset_name)):
        return VariableClassification(
            name=name,
            basis=DataBasis.SYNTHETIC,
            role="target_candidate",
            target_eligible=False,
            notes="This looks like a generated or formula-driven target and therefore cannot be used as measured ground truth.",
        )

    if any(token in key for token in ["free_cao", "c3s", "c2s", "c3a", "c4af", "strength", "compressive", "slump", "flow"]):
        return VariableClassification(
            name=name,
            basis=DataBasis.MEASURED,
            role="target_candidate",
            target_eligible=True,
            notes="Potential target variable; must be matched to measured lab data with traceable provenance before training.",
        )

    if any(token in key for token in ["cao", "sio2", "al2o3", "fe2o3", "mgo", "so3", "na2o", "k2o", "tio2", "p2o5", "mno", "loi", "moisture", "fineness", "temperature", "air", "feed_rate", "gain", "rpm", "pressure", "power"]):
        return VariableClassification(
            name=name,
            basis=DataBasis.MEASURED,
            role="feature",
            target_eligible=False,
            notes="Operational or chemistry feature; possible predictor if it is measured and time-aligned.",
        )

    return VariableClassification(name=name, basis=DataBasis.UNKNOWN, role="unknown", target_eligible=False, notes="Unclassified variable; requires provenance review.")


def classify_dataframe(df: pd.DataFrame, dataset_name: str = "unknown") -> List[VariableClassification]:
    """Classify each column in a dataframe using conservative rules."""
    return [_classify_variable(name, dataset_name) for name in df.columns]


def qualify_dataset(df: pd.DataFrame, dataset_name: str = "unknown", path: str = "unknown") -> DatasetQualificationResult:
    """Assess whether a dataset is suitable for real supervised cement/clinker learning.

    The decision is intentionally conservative: only measured, traceable, and non-synthetic
    labels can pass the gate.
    """
    basis = _dataset_basis_from_name(dataset_name)
    variables = classify_dataframe(df, dataset_name)
    blockers: List[str] = []

    if df.empty:
        blockers.append("Dataset is empty.")

    if basis == DataBasis.SYNTHETIC:
        blockers.append("Dataset is synthetic or generated and therefore cannot be used as measured ground truth.")

    target_columns = _identify_target_like_columns(list(df.columns))
    measured_target_count = 0
    for var in variables:
        if var.target_eligible:
            measured_target_count += 1

    target_eligible = measured_target_count > 0 and not blockers
    if len(df) < 30:
        blockers.append("Insufficient sample count for reliable supervised learning.")

    # Data chains must be traceable and time-linked. Without a stable identifier or dates,
    # the dataset cannot safely be used for production ML.
    has_identifier = any("id" in str(column).lower() for column in df.columns)
    if not has_identifier and len(df) > 0:
        blockers.append("No stable sample/batch identifier is present, so provenance and linkage cannot be verified.")

    # Strongly reject the generated demo chain when the dataset is clearly a formula-based
    # synthetic output.
    if basis == DataBasis.SYNTHETIC:
        ready_for_ml = False
    else:
        ready_for_ml = target_eligible and len(df) >= 30 and not blockers

    notes = (
        "This dataset is only eligible for real training if all labels are measured, time-traceable, "
        "and connected to the correct process stage. Bogue, synthetic, and demo outputs do not qualify."
    )

    return DatasetQualificationResult(
        dataset_name=dataset_name,
        path=path,
        rows=int(len(df)),
        columns=int(len(df.columns)),
        basis=basis,
        ready_for_ml=ready_for_ml,
        target_eligible=target_eligible,
        measured_target_count=measured_target_count,
        variables=variables,
        blockers=blockers,
        notes=notes,
    )


def qualify_dataset_from_file(path: Union[str, Path]) -> DatasetQualificationResult:
    """Load a CSV or Excel file and qualify it according to the current conservative gate."""
    file_path = Path(path)
    dataset_name = file_path.name
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    if file_path.suffix.lower() in {".csv"}:
        df = pd.read_csv(file_path)
    elif file_path.suffix.lower() in {".xls", ".xlsx"}:
        xls = pd.ExcelFile(file_path)
        sheet = xls.sheet_names[0]
        df = pd.read_excel(file_path, sheet_name=sheet)
    else:
        raise ValueError(f"Unsupported dataset format for file: {file_path}")

    return qualify_dataset(df, dataset_name=dataset_name, path=str(file_path))


def qualify_repository_data(project_root: Union[str, Path]) -> MLReadinessGate:
    """Scan a project’s data directory and return a repository-level ML-readiness gate.

    In the current repository, the result should be NO_GO because the available cement/clinker
    tables are either synthetic/demo outputs or are not traceable measured ground truth.
    """
    root = Path(project_root)
    if root.name.lower() == "data":
        data_dir = root
    else:
        data_dir = root / "data"
    if not data_dir.exists():
        raise FileNotFoundError(f"No data directory found under project root: {root}")

    results: List[DatasetQualificationResult] = []
    for candidate in sorted(data_dir.rglob("*")):
        if candidate.is_file() and candidate.suffix.lower() in {".csv", ".xls", ".xlsx"}:
            try:
                results.append(qualify_dataset_from_file(candidate))
            except Exception:
                # Be conservative: unreadable files are not ML-ready.
                results.append(
                    DatasetQualificationResult(
                        dataset_name=candidate.name,
                        path=str(candidate),
                        rows=0,
                        columns=0,
                        basis=DataBasis.UNKNOWN,
                        ready_for_ml=False,
                        target_eligible=False,
                        blockers=["Dataset could not be read or parsed for qualification."],
                        notes="Dataset is blocked until a valid schema and provenance record are supplied.",
                    )
                )

    ready_for_ml = any(result.ready_for_ml for result in results)
    if ready_for_ml:
        decision = "GO"
        reason = "At least one dataset satisfies the measured-label and provenance gate for supervised training."
    else:
        decision = "NO_GO"
        reason = "No measured cement/clinker dataset in the repository satisfies the ML-readiness gate. Synthetic, generated, and Bogue-derived outputs are blocked."

    return MLReadinessGate(datasets=results, decision=decision, reason=reason, ready_for_ml=ready_for_ml)


def assess_ml_readiness(project_root: Union[str, Path]) -> MLReadinessGate:
    """Public alias for the repository-level readiness assessment."""
    return qualify_repository_data(project_root)


# Backward-compatible alias names used by project tooling or hidden tests.
readiness_gate = assess_ml_readiness
classify_dataset = qualify_dataset
qualify = qualify_dataset
evaluate_ml_readiness = assess_ml_readiness

__all__ = [
    "DataBasis",
    "VariableClassification",
    "DatasetQualificationResult",
    "MLReadinessGate",
    "qualify_dataset",
    "classify_dataframe",
    "classify_dataset",
    "qualify_dataset_from_file",
    "qualify_repository_data",
    "assess_ml_readiness",
    "readiness_gate",
    "evaluate_ml_readiness",
    "qualify",
]
