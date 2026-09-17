# Provenance and Source Traceability

This section tracks the origin of each dataset and clarifies what can and cannot be claimed about the data.

## 1) `DiB - Cement Plant data.xlsx`

- Likely provenance: a case-study / inventory workbook for cement plant LCA or environmental impact work.
- Evidence from workbook content: header text refers to plant case studies and LCA inventory data; multiple sheets with environmental accounting and energy use.
- Claim to avoid: do not label this as a raw industrial plant telemetry dataset or a full production database unless additional metadata confirms a live operational system.
- Best description: case-study LCA / inventory workbook.
- Missing provenance details: plant ID, production date range, reporting period, source publication, DOI, and database schema are not fully captured in the workbook structure.

## 2) `Concrete_Data.xls`

- Likely provenance: benchmark concrete mix dataset used in popular concrete engineering regression studies.
- Evidence: clean tabular structure; names reflect known concrete recipe variables; target is compressive strength, a standard benchmark target.
- Best description: composite concrete mix design dataset.
- Missing provenance details: original publication/source is not embedded in the workbook itself.

## 3) `blended_cement_concrete_database.csv`

- Likely provenance: aggregated literature dataset assembled from multiple studies.
- Evidence: the file includes a `DOI` column and many references; this is a compiled research database rather than one plant or one site database.
- Best description: literature-derived concrete strength database.
- Key caution: this should not be treated as one source system or one production environment.

## 4) `slump_test.data`

- Provenance: UCI dataset; donor I-Cheng Yeh, Chung-Hua University.
- Evidence: `slump_test.names` states dataset donor, institution, and publication references.
- Best description: open benchmark dataset for concrete workability and strength modeling.
- License: not explicit in the file; treat as benchmark data for research use.

## 5) `slump_test.names`

- Provenance: metadata file accompanying `slump_test.data`.
- Best description: documentary metadata for the benchmark dataset.

## 6) `Raw_Materials.xlsx`

- Likely provenance: curated raw-material chemistry dataset with material types, source IDs, sample IDs, and DOI or URL metadata.
- Evidence: fields like `Source_ID`, `DOI_or_URL`, `Source_Page_Table`, `Value_Status` indicate a curated reference catalogue.
- Best description: material reference database for raw chemistry checks.
- Caution: it is a curated sample table, not a full plant-sourcing log or a daily production ledger.

## Provenance summary

The datasets do not form a single-origin operational history. They are a mix of:

- benchmark datasets,
- literature-compiled databases,
- case-study LCA workbook data,
- curated material chemistry samples.

This split matters because any attempt to force them into a single "industrial plant dataset" narrative would be scientifically inaccurate.
