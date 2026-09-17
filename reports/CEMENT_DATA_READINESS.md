# Cement Data Readiness Assessment

## Dataset inventory

The repository contains the following cement-process datasets:

- `data/raw_materials/raw_materials_database.csv` — 6 rows, chemistry reference data
- `data/raw_mix/raw_meal_samples.csv` — 1200 rows, raw meal chemistry with `Batch_ID`
- `data/clinker/clinker_analysis.csv` — 1200 rows, clinker chemistry and computed moduli
- `data/kiln_process/kiln_telemetry.csv` — 1200 rows, process telemetry for kiln operation
- `data/cement/cement_quality.csv` — 1200 rows, quality and strength outputs

## Joinability

The cement tables are linked by `Batch_ID` and are suitable for a cement-only feature pipeline.
This is an important limitation and design decision:
- cement chemistry is not merged with the concrete benchmark dataset (`Concrete_Data.xls`)
- there is no reliable join key across the concrete benchmark and the cement process tables

## Chemistry readiness

The data is ready for chemistry feature extraction because it includes the expected oxide set and process context:
- `CaO`, `SiO2`, `Al2O3`, `Fe2O3`
- optional `MgO`, `SO3`, `LOI`
- computed LSF / SM / AM in clinker table
- `Free_CaO` available in clinker chemistry
- Bogue phases available as reference values

## Model-readiness caveat

This dataset is ready for feature-layer development and process analytics, but not for arbitrary model training that mixes cement and concrete datasets or uses target-derived engineering features without explicit provenance.

## Recommended downstream use

Recommended uses:
- chemistry feature extraction
- process quality analysis
- clinker-cement relationship studies
- engineering-rule validation
- future PIML / ML with explicit feature lineage and leakage controls

Not recommended without additional work:
- cross-dataset merge with concrete benchmark data
- model training with unlabeled or ambiguous target leakage
- using Bogue phases as if they were directly measured XRD values

## Final status

The cement data is ready for the chemistry feature engineering layer and is appropriately separated from the concrete benchmark dataset.
The implementation respects the project’s scientific and engineering guardrails.
