import numpy as np
import pandas as pd

from src.preprocessing.data_preprocessing import (
    ConcretePreprocessor,
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    load_concrete_dataset,
    prepare_concrete_dataframe,
    split_features_target,
)


def test_dataset_loading_returns_expected_frame():
    df = load_concrete_dataset()
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] > 0
    assert df.shape[1] == 9


def test_expected_concrete_schema_and_target():
    df = prepare_concrete_dataframe(load_concrete_dataset())
    assert list(df.columns) == FEATURE_COLUMNS + [TARGET_COLUMN]
    assert set(FEATURE_COLUMNS).issubset(df.columns)
    assert TARGET_COLUMN in df.columns


def test_target_exists_with_feature_target_separation():
    df = prepare_concrete_dataframe(load_concrete_dataset())
    X, y = split_features_target(df)
    assert TARGET_COLUMN not in X.columns
    assert y.name == TARGET_COLUMN
    assert len(X) == len(y)


def test_duplicate_rows_are_removed():
    raw = load_concrete_dataset()
    duplicate_count = int(raw.duplicated().sum())
    cleaned = prepare_concrete_dataframe(raw)
    assert len(cleaned) == len(raw) - duplicate_count
    assert cleaned.duplicated().sum() == 0


def test_missing_values_are_handled_without_leakage():
    raw = load_concrete_dataset()
    raw.loc[0, "Water  (component 4)(kg in a m^3 mixture)"] = np.nan
    cleaned = prepare_concrete_dataframe(raw)
    assert cleaned["water"].isna().sum() >= 1

    preprocessor = ConcretePreprocessor()
    X_train, X_test, y_train, y_test = preprocessor.prepare_split(cleaned)
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    assert X_train_processed.shape == X_train.shape
    assert X_test_processed.shape == X_test.shape
    assert not np.isnan(X_train_processed.to_numpy()).any()
    assert not np.isnan(X_test_processed.to_numpy()).any()


def test_deterministic_split_is_reproducible():
    df = prepare_concrete_dataframe(load_concrete_dataset())
    first = ConcretePreprocessor().prepare_split(df)
    second = ConcretePreprocessor().prepare_split(df)

    for left, right in zip(first, second):
        pd.testing.assert_index_equal(left.index, right.index)


def test_train_test_separation_and_no_target_leakage():
    df = prepare_concrete_dataframe(load_concrete_dataset())
    X_train, X_test, y_train, y_test = ConcretePreprocessor().prepare_split(df)

    assert set(X_train.index).isdisjoint(set(X_test.index))
    assert set(y_train.index).isdisjoint(set(y_test.index))
    assert TARGET_COLUMN not in X_train.columns
    assert TARGET_COLUMN not in X_test.columns
    assert X_train.index.equals(y_train.index)
    assert X_test.index.equals(y_test.index)


def test_preprocessing_pipeline_remains_leakage_safe():
    df = prepare_concrete_dataframe(load_concrete_dataset())
    preprocessor = ConcretePreprocessor()
    X_train, X_test, y_train, y_test = preprocessor.prepare_split(df)

    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    assert X_train_processed.columns.tolist() == X_train.columns.tolist()
    assert X_test_processed.columns.tolist() == X_test.columns.tolist()
    assert y_train.name == TARGET_COLUMN
    assert y_test.name == TARGET_COLUMN
