"""Tests for the end-to-end cement process analytics pipeline."""

from pathlib import Path

from src.pipeline.cement_process_pipeline import build_cement_process_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def test_pipeline_loads_real_repository_data():
    pipeline = build_cement_process_pipeline(DATA_DIR)
    dataset = pipeline["dataset"]
    summary = pipeline["summary"]

    assert len(dataset) > 0
    assert "Batch_ID" in dataset.columns
    assert "lsf" in dataset.columns
    assert "sm" in dataset.columns
    assert "am" in dataset.columns
    assert summary["synthetic_targets_detected"] is False
    assert summary["data_source"] == "real_repository_csvs"
    assert dataset["data_status"].nunique() == 1


def test_pipeline_computes_chemistry_features():
    pipeline = build_cement_process_pipeline(DATA_DIR)
    dataset = pipeline["dataset"]
    summary = pipeline["summary"]

    assert dataset["chemistry_valid"].sum() > 0
    assert dataset["lsf"].notna().sum() > 0
    assert dataset["bogue_reference_c3s"].notna().sum() > 0
    assert summary["mean_28d_strength_mpa"] is not None
