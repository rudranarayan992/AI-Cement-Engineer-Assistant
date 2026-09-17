# REAL CLINKER ACQUISITION CHECKLIST

This checklist defines the minimum data needed to qualify an industrial or laboratory clinker dataset for the Step 12 acquisition and validation workflow.

## A. Raw materials

- Material_ID: REQUIRED
- Material_Type: REQUIRED
- Source_ID: REQUIRED
- Sampling_DateTime: REQUIRED
- Plant_ID: REQUIRED
- Chemistry values (CaO, SiO2, Al2O3, Fe2O3, MgO, SO3, Na2O, K2O, LOI): REQUIRED
- Moisture: OPTIONAL
- Other available chemistry: OPTIONAL

## B. Raw mix

- Raw_Mix_ID: REQUIRED
- Plant_ID: REQUIRED
- Mix_DateTime: REQUIRED
- Limestone_pct: REQUIRED
- Clay_pct: REQUIRED
- Iron_Corrective_pct: REQUIRED
- Silica_Corrective_pct: REQUIRED
- Other_Material_pct: OPTIONAL
- Total proportion sum check: REQUIRED

## C. Kiln/process data

- Kiln_Run_ID: REQUIRED
- Plant_ID: REQUIRED
- Kiln_ID: REQUIRED
- DateTime: REQUIRED
- Burning_Zone_Temperature: REQUIRED
- Calciner_Temperature: REQUIRED
- Kiln_Speed: REQUIRED
- Feed_Rate: REQUIRED
- Fuel_Rate: REQUIRED
- O2: REQUIRED
- CO: REQUIRED
- CO2: REQUIRED
- Cooler_Data: OPTIONAL
- Other process variables: OPTIONAL

## D. Clinker sample data

- Sample_ID: REQUIRED
- Plant_ID: REQUIRED
- Kiln_ID: REQUIRED
- Production_DateTime: REQUIRED
- Sampling_DateTime: REQUIRED
- Raw_Mix_ID: REQUIRED
- Kiln_Run_ID: REQUIRED
- Sample provenance/collection notes: OPTIONAL

## E. XRF chemistry

- CaO_wt_pct: REQUIRED
- SiO2_wt_pct: REQUIRED
- Al2O3_wt_pct: REQUIRED
- Fe2O3_wt_pct: REQUIRED
- MgO_wt_pct: REQUIRED
- SO3_wt_pct: REQUIRED
- Na2O_wt_pct: REQUIRED
- K2O_wt_pct: REQUIRED
- LOI_wt_pct: REQUIRED
- Oxide_Method: REQUIRED
- Units: REQUIRED
- Basis: REQUIRED

## F. XRD/Rietveld phase analysis

- C3S_pct: OPTIONAL if measured phase analysis is available
- C2S_pct: OPTIONAL if measured phase analysis is available
- C3A_pct: OPTIONAL if measured phase analysis is available
- C4AF_pct: OPTIONAL if measured phase analysis is available
- Phase_Method: REQUIRED when phase data are supplied
- Phase sum check: REQUIRED when phase data are supplied
- Rietveld or validated laboratory phase analysis: REQUIRED for measured phase values

## G. Free CaO

- Free_CaO_pct: REQUIRED for clinker quality assessment
- Free_CaO_Method: REQUIRED
- Units: REQUIRED

## H. Timestamps

- Production_DateTime: REQUIRED
- Sampling_DateTime: REQUIRED
- Measurement_DateTime: REQUIRED
- Residence time / production window: REQUIRED for traceability
- Sampling delay: REQUIRED when available
- Measurement delay: OPTIONAL

## I. Sample IDs

- Sample_ID: REQUIRED
- Raw_Mix_ID: REQUIRED
- Kiln_Run_ID: REQUIRED
- Material_ID: REQUIRED for raw material records
- Replicate_ID: REQUIRED when replicates exist

## J. Plant/kiln IDs

- Plant_ID: REQUIRED
- Kiln_ID: REQUIRED
- Source_ID: REQUIRED for raw material origins

## K. Measurement methods

- Oxide_Method: REQUIRED
- Phase_Method: REQUIRED if phase fractions are supplied
- Free_CaO_Method: REQUIRED
- Instrument_ID: REQUIRED
- Lab_ID: REQUIRED

## L. Provenance/license

- Data provenance: REQUIRED
- Data provider / lab / owner metadata: REQUIRED
- License / research use permission: REQUIRED for public or shared release
- Anonymization status: REQUIRED for plant data

## M. Traceability

- Raw material -> raw mix: REQUIRED
- Raw mix -> kiln run: REQUIRED
- Kiln run -> clinker sample: REQUIRED
- Sample linkage consistency: REQUIRED
- Production window explanation: REQUIRED

## Summary

- REQUIRED: necessary for qualification
- OPTIONAL: useful but not required for first acceptance
- NOT REQUIRED: not needed for a minimal acceptable dataset and should not be requested unless scientifically necessary

The project remains blocked until real, measured, traceable clinker data are supplied and validated.
