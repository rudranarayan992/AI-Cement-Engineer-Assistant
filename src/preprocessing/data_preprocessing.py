"""Concrete-data preprocessing utilities for the first baseline ML target.

This module intentionally focuses on the concrete compressive-strength dataset and keeps
all transformations reproducible and leakage-safe. Statistics used for preprocessing are
fit only on the training split.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

DEFAULT_RANDOM_SEED = 42
DEFAULT_TEST_SIZE = 0.2
TARGET_COLUMN = "compressive_strength"

RAW_COLUMN_MAP: Dict[str, str] = {
    "Cement (component 1)(kg in a m^3 mixture)": "cement",
    "Blast Furnace Slag (component 2)(kg in a m^3 mixture)": "slag",
    "Fly Ash (component 3)(kg in a m^3 mixture)": "fly_ash",
    "Water  (component 4)(kg in a m^3 mixture)": "water",
    "Superplasticizer (component 5)(kg in a m^3 mixture)": "superplasticizer",
    "Coarse Aggregate  (component 6)(kg in a m^3 mixture)": "coarse_aggregate",
    "Fine Aggregate (component 7)(kg in a m^3 mixture)": "fine_aggregate",
    "Age (day)": "age",
    "Concrete compressive strength(MPa, megapascals) ": "compressive_strength",
}

FEATURE_COLUMNS = [
    "cement",
    "slag",
    "fly_ash",
    "water",
    "superplasticizer",
    "coarse_aggregate",
    "fine_aggregate",
    "age",
]


def find_project_root() -> Path:
    """Locate the project root from the preprocessing module path."""
    current = Path(__file__).resolve()
    candidates = [
        current.parents[2],
        current.parents[1],
        current.parents[0],
    ]
    for candidate in candidates:
        if (candidate / "src").exists() and (candidate / "tests").exists():
            return candidate
    return current.parents[2]


def resolve_dataset_path(dataset_path: Optional[str | Path] = None) -> Path:
    """Resolve the benchmark concrete dataset path, preserving the original source untouched."""
    if dataset_path is not None:
        path = Path(dataset_path).expanduser().resolve()
        if path.exists():
            return path
        raise FileNotFoundError(f"Dataset not found at {path}")

    project_root = find_project_root()
    candidates = [
        project_root / "Concrete_Data.xls",
        project_root / "data" / "raw" / "Concrete_Data.xls",
        project_root / "data" / "Concrete_Data.xls",
        project_root.parent / "Concrete_Data.xls",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        "Concrete_Data.xls not found. Expected under project root or one level above it."
    )


def load_concrete_dataset(
    dataset_path: Optional[str | Path] = None,
    sheet_name: str = "Sheet1",
) -> pd.DataFrame:
    """Load the concrete benchmark dataset from the original raw Excel file."""
    path = resolve_dataset_path(dataset_path)
    data = pd.read_excel(path, sheet_name=sheet_name)
    return data


def validate_expected_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Ensure the concrete benchmark schema is present before any preprocessing occurs."""
    required_raw = list(RAW_COLUMN_MAP.keys())
    canonical_required = FEATURE_COLUMNS + [TARGET_COLUMN]

    if set(canonical_required).issubset(frame.columns):
        return frame.copy()

    missing = [column for column in required_raw if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing expected concrete columns: {missing}")
    return frame.copy()


def prepare_concrete_dataframe(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize the raw concrete schema to a canonical feature/target layout."""
    validated = validate_expected_columns(frame.copy())
    renamed = validated.rename(columns=RAW_COLUMN_MAP)
    cleaned = renamed[FEATURE_COLUMNS + [TARGET_COLUMN]].copy()

    for column in FEATURE_COLUMNS + [TARGET_COLUMN]:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="raise")

    if cleaned.isna().any().any():
        # NaNs are tolerated before train/test split; they will be handled by the fitting imputer.
        pass

    if cleaned[TARGET_COLUMN].isna().any():
        raise ValueError("Target column contains missing values; this is not allowed for the baseline dataset.")

    if (cleaned[FEATURE_COLUMNS] < 0).any().any():
        neg_cols = cleaned[FEATURE_COLUMNS].columns[(cleaned[FEATURE_COLUMNS] < 0).any()].tolist()
        raise ValueError(f"Negative values found in feature columns: {neg_cols}")

    cleaned = cleaned.drop_duplicates().reset_index(drop=True)
    return cleaned


def split_features_target(
    frame: pd.DataFrame,
    feature_columns: Optional[Sequence[str]] = None,
    target_column: str = TARGET_COLUMN,
) -> Tuple[pd.DataFrame, pd.Series]:
    """Return features and target for the baseline regression task."""
    features = list(feature_columns) if feature_columns is not None else FEATURE_COLUMNS
    if target_column not in frame.columns:
        raise ValueError(f"Target column '{target_column}' not found in the provided data.")
    if not set(features).issubset(frame.columns):
        missing = sorted(set(features) - set(frame.columns))
        raise ValueError(f"Requested feature columns missing: {missing}")
    return frame[features].copy(), frame[target_column].copy()


@dataclass
class ConcretePreprocessor:
    """Leakage-safe preprocessing pipeline for the concrete strength benchmark.

    The imputer and scaler are fitted on the training set only and then applied to the
    validation/test set. This keeps the preprocessing stage fully reproducible while
    preventing information leakage.
    """

    feature_columns: List[str] = field(default_factory=lambda: FEATURE_COLUMNS.copy())
    target_column: str = TARGET_COLUMN
    test_size: float = DEFAULT_TEST_SIZE
    random_state: int = DEFAULT_RANDOM_SEED
    _pipeline: Optional[Pipeline] = None

    def __post_init__(self) -> None:
        self._pipeline = Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )

    def fit(self, X_train: pd.DataFrame) -> "ConcretePreprocessor":
        if self._pipeline is None:
            raise ValueError("Preprocessor pipeline is not initialized.")
        self._pipeline.fit(X_train)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if self._pipeline is None:
            raise ValueError("Preprocessor pipeline is not initialized.")
        transformed = self._pipeline.transform(X)
        return pd.DataFrame(transformed, columns=X.columns, index=X.index)

    def fit_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        return self.fit(X).transform(X)

    def prepare_split(
        self,
        frame: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Prepare a reproducible train/test split after schema validation."""
        prepared = prepare_concrete_dataframe(frame)
        X, y = split_features_target(prepared, feature_columns=self.feature_columns, target_column=self.target_column)

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=self.test_size,
            random_state=self.random_state,
            shuffle=True,
        )

        return X_train, X_test, y_train, y_test

    def preprocess(
        self,
        frame: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Fit the preprocessing pipeline on the training data and transform both splits."""
        X_train, X_test, y_train, y_test = self.prepare_split(frame)
        self.fit(X_train)
        X_train_processed = self.transform(X_train)
        X_test_processed = self.transform(X_test)
        return X_train_processed, X_test_processed, y_train, y_test


def save_processed_split(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    output_dir: Optional[str | Path] = None,
) -> Path:
    """Persist the processed train/test split into a dedicated processed-data directory."""
    base_dir = Path(output_dir) if output_dir is not None else find_project_root() / "data" / "processed"
    base_dir.mkdir(parents=True, exist_ok=True)

    X_train.to_csv(base_dir / "concrete_X_train.csv", index=False)
    X_test.to_csv(base_dir / "concrete_X_test.csv", index=False)
    y_train.to_csv(base_dir / "concrete_y_train.csv", index=False, header=True)
    y_test.to_csv(base_dir / "concrete_y_test.csv", index=False, header=True)
    return base_dir


def build_concrete_preprocessing_pipeline(
    dataset_path: Optional[str | Path] = None,
    output_dir: Optional[str | Path] = None,
    random_state: int = DEFAULT_RANDOM_SEED,
    test_size: float = DEFAULT_TEST_SIZE,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, Path]:
    """Convenience function to load, validate, split, and save the concrete baseline data."""
    raw = load_concrete_dataset(dataset_path)
    preprocessor = ConcretePreprocessor(random_state=random_state, test_size=test_size)
    X_train, X_test, y_train, y_test = preprocessor.prepare_split(raw)
    preprocessor.fit(X_train)
    X_train_processed = preprocessor.transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    output_path = save_processed_split(X_train_processed, X_test_processed, y_train, y_test, output_dir)
    return X_train_processed, X_test_processed, y_train, y_test, output_path


def clean_numeric_columns(df: pd.DataFrame, columns: Iterable[str] | None = None) -> pd.DataFrame:
    """Cast selected columns to numeric types and fill missing values with a median."""
    cleaned = df.copy()
    cols = list(columns) if columns is not None else cleaned.columns.tolist()
    for column in cols:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
            median = cleaned[column].median()
            cleaned[column] = cleaned[column].fillna(median)
    return cleaned


def engineer_feature_set(df: pd.DataFrame, feature_columns: List[str]) -> pd.DataFrame:
    """Return the feature table with numeric coercion for downstream workflows."""
    features = df[feature_columns].copy()
    return clean_numeric_columns(features)


def mass_balance_raw_mix(materials: dict, proportions: dict) -> dict:
    """Compute raw-meal oxide composition from input materials and mass proportions."""
    props = {k: float(v) for k, v in proportions.items()}
    total = sum(props.values())
    if total == 0:
        raise ValueError("Sum of proportions must be > 0")
    if total > 1.0:
        props = {k: v / total for k, v in props.items()}

    oxide_keys = set()
    for material in materials.values():
        oxide_keys.update(material.keys())

    aggregated = {oxide: 0.0 for oxide in oxide_keys}
    for mat_id, frac in props.items():
        mat = materials.get(mat_id, {})
        for oxide in oxide_keys:
            aggregated[oxide] += float(mat.get(oxide, 0.0)) * frac

    return aggregated


def clr_transform(df: pd.DataFrame, oxide_columns: List[str], eps: float = 1e-6) -> pd.DataFrame:
    """Apply a centered log-ratio transform to oxide composition columns."""
    comp = df[oxide_columns].astype(float).copy()
    comp = comp.clip(lower=eps)
    row_sums = comp.sum(axis=1)
    comp_frac = comp.div(row_sums, axis=0)
    gm = np.exp(np.log(comp_frac).mean(axis=1))
    clr_vals = np.log(comp_frac.div(gm, axis=0))
    clr_vals.index = df.index
    return clr_vals


def check_closure(df: pd.DataFrame, oxide_columns: List[str], tol: float = 1e-3) -> pd.Series:
    """Return booleans indicating whether oxide totals are approximately closed."""
    sums = df[oxide_columns].sum(axis=1)
    target = 100.0 if (sums.mean() > 1.1) else 1.0
    return (sums - target).abs() <= tol
