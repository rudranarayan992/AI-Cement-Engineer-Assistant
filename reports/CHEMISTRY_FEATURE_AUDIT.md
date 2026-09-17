# Chemistry Feature Audit

## Scope

This audit covers the cement chemistry feature engineering layer introduced in `src/features/chemistry_features.py`.

The scope is intentionally limited to:
- cement chemistry feature extraction
- provenance and leakage tracking
- basis handling and validation
- no model training
- no concrete benchmark merge
- no synthetic data generation

## Data sources used

The chemistry feature layer operates on cement process datasets already present in the repository:

- `data/raw_materials/raw_materials_database.csv`
- `data/raw_mix/raw_meal_samples.csv`
- `data/clinker/clinker_analysis.csv`
- `data/kiln_process/kiln_telemetry.csv`
- `data/cement/cement_quality.csv`

Important guardrail:
- The cement datasets are linked by `Batch_ID`.
- The `Concrete_Data.xls` benchmark remains separate and is not merged with cement chemistry data.

## Features implemented

### 1. LSF (lime saturation factor)
- Formula: `CaO / (2.8 * SiO2 + 1.18 * Al2O3 + 0.65 * Fe2O3)`
- Basis assumption: ignited basis
- Classification: `SAFE`
- Leakage risk: low, because it is a direct chemistry ratio and not a target-derived variable

### 2. SM (silica modulus)
- Formula: `SiO2 / (Al2O3 + Fe2O3)`
- Basis assumption: ignited basis
- Classification: `SAFE`

### 3. AM (alumina modulus)
- Formula: `Al2O3 / Fe2O3`
- Basis assumption: ignited basis
- Classification: `SAFE`

### 4. Bogue reference phases
- `bogue_reference_c3s`
- `bogue_reference_c2s`
- `bogue_reference_c3a`
- `bogue_reference_c4af`
- Rule: labeled as `reference` and not treated as measured XRD phase labels.
- Classification: `CONDITIONAL`
- Purpose: engineering benchmark only

## Provenance model

Each feature is accompanied by a `FeatureProvenance` record containing:
- feature name
- source variables
- formula
- basis
- units
- method (`computed`, `reference`)
- target-derived flag
- leakage risk
- notes
- source dataset name

This makes the feature layer traceable and auditable for downstream use.

## Basis handling

The feature layer follows the project rule:
- do not silently convert basis values
- if input includes `LOI`, ignited-basis conversion is performed explicitly
- otherwise the implementation warns that values are assumed to already be ignited-basis

This avoids hidden data leakage and keeps chemistry semantics transparent.

## Validation behavior

The implementation integrates with the existing `physics_constraints` layer:
- negative oxide values are rejected
- missing oxide values produce NaN features
- infinity and NaN values fail fast
- validation warnings are captured in structured outputs

## Leakage audit

Feature leakage classification is explicit:
- `SAFE`: LSF, SM, AM
- `CONDITIONAL`: Bogue reference phases

The Bogue phases are intentionally not presented as direct measured targets or measured phase labels.
They are benchmark features only.

## Final assessment

The chemistry feature engineering layer is ready as a reusable, provenance-aware interface for future modeling work.
It respects the project constraints:
- no concrete merge
- no model training
- no synthetic data
- no data leakage through target-derived features
