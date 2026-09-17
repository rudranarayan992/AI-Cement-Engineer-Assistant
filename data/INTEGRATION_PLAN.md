# Integration Plan

The available datasets should not be forced into one master table.

## 1) Datasets that can remain independent

These datasets are best kept separate because they represent different measurement regimes and lack reliable cross-source keys:

- `DiB - Cement Plant data.xlsx` -> environmental / LCA inventory case study
- `Raw_Materials.xlsx` -> material chemistry reference set
- `slump_test.data` + `slump_test.names` -> workability benchmark dataset
- `Concrete_Data.xls` -> concrete strength benchmark dataset
- `blended_cement_concrete_database.csv` -> literature-derived strength database

## 2) Datasets that may be connected within a narrow scope

Only within a narrow domain can some connections be legitimate:

- `slump_test.data` with `slump_test.names` -> direct metadata pairing
- `Concrete_Data.xls` with the concrete mix literature database -> both are concrete-recipe datasets, but the schema is not identical and therefore should not be merged blindly
- `Raw_Materials.xlsx` with a separately created raw-mix recipe table -> only if a real and documented blend recipe exists and a proper material matching system is implemented

## 3) Datasets that should not be merged

These should remain distinct because there is no reliable join key between them:

- raw materials chemistry table vs. concrete strength tables
- concrete strength tables vs. environmental inventory workbook
- plant LCA workbook vs. benchmark concrete datasets
- any dataset without consistent `Sample_ID`, `Batch_ID`, `Plant_ID`, `Mix_ID`, or date/time alignment

## 4) Join key assessment

The project should explicitly record:

- `NO RELIABLE JOIN KEY` across the full dataset set

Reason:

- different data domains (materials, concrete mix design, LCA inventory)
- no common sample identifiers
- no common plant or batch IDs across datasets
- no time-aligned production records

## 5) Recommended integration structure

Use separate modules or tables for each domain:

1. `raw_material_reference`
2. `concrete_recipe_benchmark`
3. `slump_workability_dataset`
4. `environmental_inventory_case_study`
5. `raw_material_chemistry_samples`

Only create a combined table if a new, legitimate, and documented traceability key is introduced by future data collection.

## 6) Practical recommendation

Do not attempt a full chain merge. The scientifically valid approach is:

- keep each dataset independent,
- link only within a domain where clear provenance and schema match,
- use data lineage and provenance metadata to prevent false joins.

This is preferable to a forced master table that would create spurious correlations and leakage risk.
