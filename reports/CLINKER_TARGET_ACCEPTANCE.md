# CLINKER TARGET ACCEPTANCE

This document classifies potential target variables based strictly on the actual supplied dataset and measured provenance. It does not assume a target exists.

## Classification legend

- READY: acceptable for supervised modeling only when supplied as measured data with valid provenance and traceability
- CONDITIONAL: may be usable with stronger validation, documentation, and traceability
- NOT_READY: not acceptable as scientific target data in the current project state

## Target assessment

| Target | Status | Reason |
|---|---|---|
| Free_CaO | CONDITIONAL if measured; otherwise NOT_READY | Valid only when directly measured by an accepted laboratory method and linked to a production record |
| C3S_pct | CONDITIONAL if measured by XRD/Rietveld or validated phase method; otherwise NOT_READY | Bogue values are not measured phase ground truth |
| C2S_pct | CONDITIONAL if measured by XRD/Rietveld or validated phase method; otherwise NOT_READY | Bogue values are not measured phase ground truth |
| C3A_pct | CONDITIONAL if measured by XRD/Rietveld or validated phase method; otherwise NOT_READY | Bogue values are not measured phase ground truth |
| C4AF_pct | CONDITIONAL if measured by XRD/Rietveld or validated phase method; otherwise NOT_READY | Bogue values are not measured phase ground truth |
| Clinker oxide chemistry | CONDITIONAL if measured by XRF and fully traceable | Acceptable for measured chemistry, not for direct phase measurement |

## Acceptance rule

A target is considered usable for project research only if all of the following are true:

- the measurement method is documented
- the target is linked to a definite clinker sample ID
- timestamps and plant/kiln linkage are present
- provenance is documented
- the target is not a Bogue-derived synthetic label
- the dataset is not generated via formula-only simulation

## Current project status

The repository remains under Step 12 blocked status because no qualified plant-linked measured clinker dataset has been supplied.
