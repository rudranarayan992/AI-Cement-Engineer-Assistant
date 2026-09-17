# Real Clinker Data Request Specification v2

## Purpose

This document defines the minimum information required to evaluate a real clinker dataset for a scientifically valid research program. The purpose is to support measured clinker quality analysis, raw-material/process traceability, and future model development only after a dataset passes the acceptance gate.

This request is intentionally limited to real measured data and does not permit synthetic targets, Bogue-derived labels, or inferred clinker quality as ground truth.

## Required dataset structure

### A. Raw materials

Each raw material record should include:

- Material_ID
- Material_Type
- Sampling_DateTime
- Source_Lot_ID
- Plant_ID (if relevant)
- CaO
- SiO2
- Al2O3
- Fe2O3
- MgO
- SO3
- Na2O
- K2O
- LOI
- Moisture
- physical properties where available

Required metadata:

- measurement method
- instrument or lab method
- units
- basis (as_received, dry, ignited)
- replicate count if repeated measurements exist
- sample handling or preparation notes if relevant

### B. Raw mix

Each raw-mix record should include:

- Raw_Mix_ID
- Plant_ID
- Raw_Mix_DateTime
- material proportions
- raw meal chemistry
- LSF
- SM
- AM

Required metadata:

- recipe source or formulation basis
- proportion units
- whether values are as-batched or as-fed
- process or blend notes
- QA/QC flag if applicable

### C. Kiln process

Each kiln process record should include:

- Kiln_Run_ID
- Plant_ID
- Kiln_ID
- DateTime
- kiln temperature
- calciner temperature
- feed rate
- fuel rate
- O2
- CO
- CO2
- kiln speed
- draft/pressure
- secondary air temperature
- cooler variables
- other available DCS variables

Required metadata:

- sensor ID where available
- sampling interval
- calibration status
- units
- operating regime or product grade
- any process disturbances or kiln interruptions

### D. Clinker

Each clinker record should include:

- Clinker_Sample_ID
- Production_DateTime
- Sampling_DateTime
- Measurement_DateTime
- Plant_ID
- Kiln_ID
- Raw_Mix_ID
- Kiln_Run_ID

Required metadata:

- sampling method
- location of sample within clinker production stream
- grade or product type
- sample storage or preparation information

### E. Measured clinker quality

#### XRF chemistry

- CaO
- SiO2
- Al2O3
- Fe2O3
- MgO
- SO3
- Na2O
- K2O
- LOI

#### Laboratory quality

- Free_CaO

#### Phase analysis

- C3S
- C2S
- C3A
- C4AF

Required metadata:

- instrument model
- method/standard reference
- calibration material
- replicate/instrument run ID
- analyst or lab identifier
- units and basis
- QC or QA status

### F. Measurement metadata

Every measured value should carry:

- measurement method
- instrument
- laboratory
- units
- basis
- standard or method reference
- replicate information
- quality flags
- calibration status
- measurement date/time

## Data governance expectations

- The dataset may be shared in anonymized form.
- Company names, confidential recipes, or production details are not required.
- Relational keys and timestamps must be preserved.
- If confidentiality is required, use anonymized identifiers such as Plant_A, Kiln_1, RawMix_001, Clinker_000001.

## Minimum acceptable intake package

A dataset should include at minimum:

1. Material assay data
2. Raw-mix proportion data
3. Process or kiln telemetry aligned to the clinker sample
4. Measured clinker chemistry and phase data
5. Clear attribution of which values are measured versus calculated

## Research use statement

This request is for a measured data package suitable for scientific review and future model development only after the project’s acceptance gate is passed. No model training or prediction work is requested in this step.
