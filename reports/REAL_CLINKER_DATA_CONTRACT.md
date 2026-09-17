# REAL CLINKER DATA CONTRACT

## Scope

This contract defines the minimum acceptable industrial clinker dataset for the main research track. It is designed for plant-linked research and must support a valid raw-material -> raw-mix -> kiln process -> clinker sample chain.

This is not a synthetic dataset contract. It is a measured-data contract for scientific use.

## Minimum acceptable clinker table

Required columns for each clinker sample:

- Sample_ID
- Plant_ID
- Kiln_ID
- Production_DateTime
- Sampling_DateTime
- Raw_Mix_ID
- Kiln_Run_ID

Measured clinker chemistry:

- CaO_wt_pct
- SiO2_wt_pct
- Al2O3_wt_pct
- Fe2O3_wt_pct
- MgO_wt_pct
- SO3_wt_pct
- Na2O_wt_pct
- K2O_wt_pct
- LOI_wt_pct

Measured clinker quality:

- Free_CaO_pct

Measured clinker phases, if available:

- C3S_pct
- C2S_pct
- C3A_pct
- C4AF_pct

Measurement metadata:

- Phase_Method
- Oxide_Method
- Free_CaO_Method
- Lab_ID
- Instrument_ID
- Measurement_DateTime
- Replicate_ID
- Units
- Basis

## Acceptance rules

A clinker dataset is acceptable for the main industrial research track only if all conditions below are met:

1. Each record has a unique `Sample_ID`.
2. `Plant_ID` and `Kiln_ID` are present and consistent with the production system.
3. `Production_DateTime` and `Sampling_DateTime` are valid timestamps.
4. `Raw_Mix_ID` and `Kiln_Run_ID` are supplied and traceable to upstream tables.
5. Oxide chemistry is reported as measured wt% values with a documented oxide method.
6. XRF may be used for clinker oxide chemistry only.
7. XRF must not be described as direct measurement of C3S/C2S/C3A/C4AF phase fractions.
8. Phase fractions require an appropriate phase-analysis method, such as XRD, Rietveld, or a validated laboratory method.
9. Free CaO is reported as a measured clinker quality metric with a documented method.
10. Units and basis are explicitly documented.
11. Provenance is documented through `Lab_ID`, `Instrument_ID`, `Measurement_DateTime`, and replicate metadata.
12. The dataset includes a clear production/sampling relationship and traceability to actual raw material and kiln process records.

## Valid phase methods

Acceptable examples include:

- XRD
- Rietveld
- validated laboratory phase analysis
- SEM/image analysis where scientifically appropriate

## Not allowed as measured phase ground truth

The following may be used only as reference or benchmark values, not as measured target labels:

- Bogue-calculated phase fractions
- synthetic phase calculations generated from the same oxide chemistry
- formula-generated labels without measured laboratory provenance

## Minimum research status

The dataset is considered qualified only when it satisfies both:

- plant-linked traceability from raw material -> raw mix -> kiln -> clinker sample
- measured chemistry and, where applicable, measured phase composition with documented methods and provenance

Until this is achieved, the project remains in Step 12 blocked status.
