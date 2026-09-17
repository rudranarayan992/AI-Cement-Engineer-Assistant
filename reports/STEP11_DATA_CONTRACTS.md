# STEP 11 — Future Data Contracts

## Purpose

The architecture defines typed interfaces for future cement/clinker machine learning without fabricating labels or modifying raw datasets.

## Data contract catalog

- RawMaterialRecord
- RawMixRecord
- KilnFeedRecord
- ProcessRecord
- HotMealRecord
- ClinkerMeasurement
- CementMeasurement
- MLTrainingRecord
- MLPrediction
- PredictionMetadata
- OODResult
- UncertaintyResult
- ValidationResult

## Provenance requirements

Each record preserves traceability fields where available:
- plant_id
- line_id
- kiln_id
- batch_id
- sample_id
- timestamp
- source_file
- measurement_method
- data_status
- basis
- unit metadata

The architecture intentionally does not invent missing identifiers. Unknown values remain optional and explicitly marked as such.

## Example data property expectations

- Raw materials include chemistry, source, and batch metadata.
- Raw mix records include recipe proportions and derived chemistry values on clear basis assumptions.
- Process records include telemetry and explicit residence-time configuration.
- Clinker records use measured XRF/XRD lab values only when those data are available.
- Cement records capture downstream product properties.

## Current implementation

These interfaces are implemented in `src/future_ml/cement_ml_architecture.py` and are ready to accept real measured industrial data later.

## Blocker

No real industrial cement/clinker measurement dataset exists in this repository, so these contracts remain future-ready interfaces rather than validated training datasets.
