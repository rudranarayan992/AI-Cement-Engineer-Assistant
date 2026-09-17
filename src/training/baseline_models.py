"""Baseline regression training for the concrete compressive-strength task.

This module intentionally implements only the first benchmark model suite for the
concrete mix design dataset used in Step 8. It does not implement optimization,
PIML, SHAP, or any industrial interpretation layer.
"""

from __future__ import annotations

import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

try:
    import xgboost as xgb
    _HAS_XGB = True
except ImportError:
    xgb = None
    _HAS_XGB = False

from src.preprocessing.data_preprocessing import (
    DEFAULT_RANDOM_SEED,
    DEFAULT_TEST_SIZE,
    ConcretePreprocessor,
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    find_project_root,
    load_concrete_dataset,
    prepare_concrete_dataframe,
)

DEFAULT_CV_FOLDS = 5


def _compute_regression_metrics(y_true: Sequence[float], y_pred: Sequence[float]) -> Dict[str, float]:
    """Compute MAE, RMSE, and R² metrics for regression."""
    y_true_arr = np.asarray(y_true, dtype=float)
    y_pred_arr = np.asarray(y_pred, dtype=float)
    return {
        "mae": float(mean_absolute_error(y_true_arr, y_pred_arr)),
        "rmse": float(np.sqrt(mean_squared_error(y_true_arr, y_pred_arr))),
        "r2": float(r2_score(y_true_arr, y_pred_arr)),
    }


def get_model_factories() -> Dict[str, Any]:
    """Return a mapping of model names to sklearn Pipelines for baseline training."""
    factories: Dict[str, Any] = {
        "ridge": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("model", Ridge(alpha=1.0)),
            ]
        ),
        "random_forest": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("model", RandomForestRegressor(n_estimators=300, random_state=DEFAULT_RANDOM_SEED, n_jobs=-1)),
            ]
        ),
        "svr": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("model", SVR(kernel="rbf", C=10.0, epsilon=0.1, gamma="scale")),
            ]
        ),
    }

    if _HAS_XGB:
        factories["xgboost"] = Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                (
                    "model",
                    xgb.XGBRegressor(
                        objective="reg:squarederror",
                        n_estimators=500,
                        max_depth=6,
                        learning_rate=0.05,
                        subsample=0.9,
                        colsample_bytree=0.9,
                        random_state=DEFAULT_RANDOM_SEED,
                        n_jobs=-1,
                        verbosity=0,
                    ),
                ),
            ]
        )

    return factories


def load_baseline_split(
    dataset_path: Optional[str | Path] = None,
    random_seed: int = DEFAULT_RANDOM_SEED,
    test_size: float = DEFAULT_TEST_SIZE,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Load the raw concrete dataset and produce a leakage-safe train/test split."""
    raw = load_concrete_dataset(dataset_path)
    prepared = prepare_concrete_dataframe(raw)
    preprocessor = ConcretePreprocessor(test_size=test_size, random_state=random_seed)
    X_train, X_test, y_train, y_test = preprocessor.prepare_split(prepared)
    preprocessor.fit(X_train)
    X_train_processed = preprocessor.transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    return X_train_processed, X_test_processed, y_train, y_test


def cross_validate_model(
    model: Any,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_splits: int = DEFAULT_CV_FOLDS,
    random_state: int = DEFAULT_RANDOM_SEED,
) -> Dict[str, list]:
    """Run k-fold cross-validation on a model."""
    kfold = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    folds: Dict[str, list] = {"mae": [], "rmse": [], "r2": []}

    for train_idx, valid_idx in kfold.split(X_train):
        fold_model = clone(model)
        fold_model.fit(X_train.iloc[train_idx], y_train.iloc[train_idx])
        predictions = fold_model.predict(X_train.iloc[valid_idx])
        metrics = _compute_regression_metrics(y_train.iloc[valid_idx], predictions)
        folds["mae"].append(metrics["mae"])
        folds["rmse"].append(metrics["rmse"])
        folds["r2"].append(metrics["r2"])

    return folds


def summarize_cv_results(cv_scores: Dict[str, list]) -> Dict[str, float]:
    """Summarize cross-validation results with mean and standard deviation."""
    return {
        "cv_mae_mean": float(np.mean(cv_scores["mae"])),
        "cv_mae_std": float(np.std(cv_scores["mae"], ddof=0)),
        "cv_rmse_mean": float(np.mean(cv_scores["rmse"])),
        "cv_rmse_std": float(np.std(cv_scores["rmse"], ddof=0)),
        "cv_r2_mean": float(np.mean(cv_scores["r2"])),
        "cv_r2_std": float(np.std(cv_scores["r2"], ddof=0)),
    }


def save_model_metadata(
    model_name: str,
    model_path: Path,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    cv_summary: Dict[str, float],
    test_metrics: Dict[str, float],
    random_seed: int = DEFAULT_RANDOM_SEED,
    preprocessing_method: str = "median imputer + StandardScaler for Ridge/SVR; median imputer only for RF",
    cross_validation_method: str = "5-fold KFold(shuffle=True, random_state=42)",
    dataset_name: str = "Concrete_Data.xls",
    target_name: str = TARGET_COLUMN,
) -> Path:
    """Persist metadata for a trained model as JSON sidecar."""
    metadata = {
        "model_name": model_name,
        "dataset_name": dataset_name,
        "target": target_name,
        "feature_names": list(X_train.columns),
        "training_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "random_seed": int(random_seed),
        "preprocessing_method": preprocessing_method,
        "cross_validation_method": cross_validation_method,
        "metrics": {
            **cv_summary,
            "test_mae": float(test_metrics["mae"]),
            "test_rmse": float(test_metrics["rmse"]),
            "test_r2": float(test_metrics["r2"]),
        },
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "sklearn_version": __import__("sklearn").__version__,
        "pandas_version": pd.__version__,
        "joblib_version": joblib.__version__,
        "xgboost_version": xgb.__version__ if xgb is not None else "not-installed",
    }

    metadata_path = model_path.with_suffix(".json")
    with metadata_path.open("w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2)
    return metadata_path


def run_baseline_training(
    dataset_path: Optional[str | Path] = None,
    random_seed: int = DEFAULT_RANDOM_SEED,
    test_size: float = DEFAULT_TEST_SIZE,
    cv_folds: int = DEFAULT_CV_FOLDS,
    output_dir: Optional[str | Path] = None,
    report_path: Optional[str | Path] = None,
) -> pd.DataFrame:
    """Train the configured baseline regression models and save artifacts plus results."""
    X_train, X_test, y_train, y_test = load_baseline_split(dataset_path, random_seed=random_seed, test_size=test_size)

    model_factories = get_model_factories()
    results: list = []

    models_dir = Path(output_dir) if output_dir is not None else find_project_root() / "models" / "baseline"
    reports_dir = Path(report_path).parent if report_path is not None else find_project_root() / "reports"
    models_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    for model_name, model in model_factories.items():
        cv_scores = cross_validate_model(model, X_train, y_train, n_splits=cv_folds, random_state=random_seed)
        cv_summary = summarize_cv_results(cv_scores)

        fitted_model = clone(model)
        fitted_model.fit(X_train, y_train)
        predictions = fitted_model.predict(X_test)
        test_metrics = _compute_regression_metrics(y_test, predictions)

        model_file = models_dir / f"{model_name}_model.joblib"
        joblib.dump(fitted_model, model_file)
        save_model_metadata(
            model_name=model_name,
            model_path=model_file,
            X_train=X_train,
            X_test=X_test,
            y_train=y_train,
            y_test=y_test,
            cv_summary=cv_summary,
            test_metrics=test_metrics,
            random_seed=random_seed,
        )

        results.append(
            {
                "model": model_name,
                "cv_mae_mean": cv_summary["cv_mae_mean"],
                "cv_mae_std": cv_summary["cv_mae_std"],
                "cv_rmse_mean": cv_summary["cv_rmse_mean"],
                "cv_rmse_std": cv_summary["cv_rmse_std"],
                "cv_r2_mean": cv_summary["cv_r2_mean"],
                "cv_r2_std": cv_summary["cv_r2_std"],
                "test_mae": test_metrics["mae"],
                "test_rmse": test_metrics["rmse"],
                "test_r2": test_metrics["r2"],
            }
        )

    results_df = pd.DataFrame(results)
    reports_path = Path(report_path) if report_path is not None else reports_dir / "baseline_model_results.csv"
    results_df.to_csv(reports_path, index=False)

    return results_df
