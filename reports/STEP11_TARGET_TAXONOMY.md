# STEP 11 — Future Cement/Clinker Target Taxonomy

## Rule

Only measured experimental values may be used as future supervised-learning ground truth.

## Allowed ground-truth categories

MEASURED_XRF
MEASURED_XRD
MEASURED_RIETVELD
MEASURED_LAB

Reference and derived categories are not valid model targets:

BOGUE_CALCULATED
CHEMISTRY_DERIVED
SYNTHETIC

## Primary clinker targets

1. Free CaO / f-CaO
   - Unit: %
   - Measurement: lab or XRF-based chemistry analysis
   - Ground truth: MEASURED_LAB / MEASURED_XRF
   - Prediction stage: clinker production
   - Online suitability: yes, if available before target is produced

2. C3S / alite
   - Unit: %
   - Measurement: XRD or Rietveld phase analysis
   - Ground truth: MEASURED_XRD / MEASURED_RIETVELD
   - Prediction stage: clinker production
   - Online suitability: not if phase data are only available after production

3. C2S / belite
   - Unit: %
   - Measurement: XRD or Rietveld phase analysis
   - Ground truth: MEASURED_XRD / MEASURED_RIETVELD
   - Prediction stage: clinker production
   - Online suitability: no for online control when lab results arrive later

4. C3A / aluminate
   - Unit: %
   - Measurement: XRD or Rietveld phase analysis
   - Ground truth: MEASURED_XRD / MEASURED_RIETVELD
   - Prediction stage: clinker production
   - Online suitability: no for online control

5. C4AF / ferrite
   - Unit: %
   - Measurement: XRD or Rietveld phase analysis
   - Ground truth: MEASURED_XRD / MEASURED_RIETVELD
   - Prediction stage: clinker production
   - Online suitability: no for online control

## Downstream targets

- clinker oxide composition
- cement fineness
- setting time
- soundness
- cement/mortar/concrete strength

These are downstream product-quality targets and should be modeled separately from kiln feed and clinker chemistry targets.

## Leakage risk summary

- Bogue values are empirical estimates, not measured phase labels.
- Synthetic labels are demo-only and must never be used as training targets.
- Post-production lab measurements must not be used in an online model that does not have access to them at prediction time.

## Current implementation

The module `src/future_ml/cement_ml_architecture.py` defines this taxonomy and enforces the measured-vs-derived rule at the interface level.
