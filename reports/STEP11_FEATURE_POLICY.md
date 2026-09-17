# STEP 11 — Feature Availability Policy

## Policy principle

Features must be separated according to when they become available relative to the production target.

## LEVEL A — ONLINE CONTROL / PREDICTION FEATURES

These are valid for future online model design when they are available before the target is produced.

Examples:
- raw-material chemistry
- raw-mix proportions
- kiln-feed chemistry
- LSF
- SM
- AM
- kiln/process telemetry
- fuel and process state variables
- valid hot-meal variables when temporally aligned and available before the target timestamp

## LEVEL B — POST-PRODUCTION DIAGNOSTIC FEATURES

These are only available after target production or laboratory testing.

Examples:
- clinker XRF oxide composition
- clinker XRD or Rietveld phase fractions
- Blaine or cement fineness test results
- setting-time measurements
- soundness measurements
- strength tests after curing

These features may be used for offline diagnostic models only, and only when the prediction task is properly defined and time-aligned.

## Policy table summary

| Feature | Level | Online eligible | Leakage risk |
| --- | --- | --- | --- |
| raw_material_chemistry | A | Yes | Low |
| raw_mix_proportions | A | Yes | Low |
| kiln_feed_chemistry | A | Yes | Low |
| LSF | A | Yes | Low |
| SM | A | Yes | Low |
| AM | A | Yes | Low |
| kiln_telemetry | A | Yes | Medium |
| clinker_xrf_oxide | B | No | High |
| clinker_xrd_phase | B | No | High |
| cement_strength_test | B | No | High |

## Current implementation

The `FeaturePolicy` and `FeaturePolicyEntry` interfaces in `src/future_ml/cement_ml_architecture.py` enforce the online/post-production separation at the schema level.

## Requirement status

The architecture is ready to accept real industrial data with a documented feature policy. It remains blocked until real measured plant and lab data are available.
