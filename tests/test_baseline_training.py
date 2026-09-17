import numpy as np
import pandas as pd
import pytest

from src.training.baseline_models import (
    DEFAULT_CV_FOLDS,
    get_model_factories,
    load_baseline_split,
    cross_validate_model,
    run_baseline_training,
)


class TestDataLoading:
    """Test baseline dataset loading and splitting."""

    def test_load_baseline_split_returns_four_arrays(self):
        X_train, X_test, y_train, y_test = load_baseline_split()
        assert isinstance(X_train, pd.DataFrame)
        assert isinstance(X_test, pd.DataFrame)
        assert isinstance(y_train, pd.Series)
        assert isinstance(y_test, pd.Series)

    def test_load_baseline_split_expected_sizes(self):
        X_train, X_test, y_train, y_test = load_baseline_split(test_size=0.2)
        total_samples = len(X_train) + len(X_test)
        assert len(X_train) == len(y_train)
        assert len(X_test) == len(y_test)
        assert total_samples == 1005

    def test_load_baseline_split_no_target_leakage(self):
        X_train, X_test, y_train, y_test = load_baseline_split()
        assert "compressive_strength" not in X_train.columns
        assert "compressive_strength" not in X_test.columns

    def test_load_baseline_split_train_test_separation(self):
        X_train, X_test, y_train, y_test = load_baseline_split()
        assert set(X_train.index).isdisjoint(set(X_test.index))
        assert set(y_train.index).isdisjoint(set(y_test.index))

    def test_load_baseline_split_deterministic_with_seed(self):
        X_train1, X_test1, y_train1, y_test1 = load_baseline_split(random_seed=42)
        X_train2, X_test2, y_train2, y_test2 = load_baseline_split(random_seed=42)
        pd.testing.assert_index_equal(X_train1.index, X_train2.index)
        pd.testing.assert_index_equal(X_test1.index, X_test2.index)


class TestModelFactories:
    """Test the model factory setup."""

    def test_model_factories_returns_dict(self):
        factories = get_model_factories()
        assert isinstance(factories, dict)
        assert len(factories) >= 3

    def test_model_factories_contains_ridge(self):
        factories = get_model_factories()
        assert "ridge" in factories

    def test_model_factories_contains_random_forest(self):
        factories = get_model_factories()
        assert "random_forest" in factories

    def test_model_factories_contains_svr(self):
        factories = get_model_factories()
        assert "svr" in factories

    def test_model_factories_xgboost_optional(self):
        factories = get_model_factories()
        if "xgboost" in factories:
            assert factories["xgboost"] is not None


class TestCrossValidation:
    """Test cross-validation and metric computation."""

    def test_cross_validate_model_returns_dict_with_metrics(self):
        X_train, _, y_train, _ = load_baseline_split()
        factories = get_model_factories()
        model = factories["ridge"]
        cv_results = cross_validate_model(model, X_train, y_train, n_splits=3)
        assert isinstance(cv_results, dict)
        assert "mae" in cv_results
        assert "rmse" in cv_results
        assert "r2" in cv_results

    def test_cross_validate_model_fold_counts(self):
        X_train, _, y_train, _ = load_baseline_split()
        factories = get_model_factories()
        model = factories["ridge"]
        n_splits = 3
        cv_results = cross_validate_model(model, X_train, y_train, n_splits=n_splits)
        assert len(cv_results["mae"]) == n_splits
        assert len(cv_results["rmse"]) == n_splits
        assert len(cv_results["r2"]) == n_splits

    def test_cross_validate_model_deterministic(self):
        X_train, _, y_train, _ = load_baseline_split()
        factories = get_model_factories()
        model = factories["ridge"]
        cv1 = cross_validate_model(model, X_train, y_train, n_splits=3, random_state=42)
        cv2 = cross_validate_model(model, X_train, y_train, n_splits=3, random_state=42)
        np.testing.assert_array_almost_equal(cv1["mae"], cv2["mae"])
        np.testing.assert_array_almost_equal(cv1["rmse"], cv2["rmse"])
        np.testing.assert_array_almost_equal(cv1["r2"], cv2["r2"])


class TestBaselineTraining:
    """Test end-to-end baseline training."""

    def test_run_baseline_training_returns_dataframe(self):
        results = run_baseline_training(cv_folds=2)
        assert isinstance(results, pd.DataFrame)
        assert len(results) >= 3

    def test_run_baseline_training_expected_columns(self):
        results = run_baseline_training(cv_folds=2)
        expected_cols = [
            "model",
            "cv_mae_mean",
            "cv_mae_std",
            "cv_rmse_mean",
            "cv_rmse_std",
            "cv_r2_mean",
            "cv_r2_std",
            "test_mae",
            "test_rmse",
            "test_r2",
        ]
        for col in expected_cols:
            assert col in results.columns

    def test_run_baseline_training_no_nan_metrics(self):
        results = run_baseline_training(cv_folds=2)
        assert not results.isna().any().any()

    def test_run_baseline_training_creates_model_files(self, tmp_path):
        results = run_baseline_training(cv_folds=2, output_dir=tmp_path)
        model_files = list(tmp_path.glob("*_model.joblib"))
        assert len(model_files) >= 3

    def test_run_baseline_training_creates_metadata_files(self, tmp_path):
        results = run_baseline_training(cv_folds=2, output_dir=tmp_path)
        metadata_files = list(tmp_path.glob("*_model.json"))
        assert len(metadata_files) >= 3
