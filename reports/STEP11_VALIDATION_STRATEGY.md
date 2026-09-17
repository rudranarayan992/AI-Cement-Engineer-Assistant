# STEP 11 — Future Validation Strategy

## Rule

Do not use random splitting as the default for industrial cement/clinker datasets.

## Required split strategies

1. Chronological train/validation/test split
   - Use when the process is time-dependent and the dataset has a natural sequence.
   - Prevents future-to-past leakage.

2. Forward or rolling validation
   - Use when the process evolves over time.
   - Helps quantify drift and concept shift.

3. Plant-wise split
   - Use when data come from multiple plants and the model must generalize across sites.

4. Kiln/line-wise split
   - Use when each kiln or line has distinct operating behavior.

## Leakage protections

The architecture explicitly prevents:
- future-to-past leakage
- test-set contamination
- preprocessing leakage
- target-derived feature leakage

## Temporal-Aware Interface

The new `TemporalAlignmentConfig` and `ChronologicalSplitConfig` objects enforce a configuration-first workflow. They require explicit residence time and chronological ordering before a model pipeline is considered valid.

## Future implementation guidance

- Always align telemetry to target timestamps using plant-specific residence time.
- Never rely on nearest-timestamp joins alone when vessel residence time is material.
- Keep preprocessing statistics computed only on the training split.
- Validate all engineered features against the allowed feature policy.

## Current implementation

The future interface is implemented in `src/future_ml/cement_ml_architecture.py` and is ready for real industrial data, but no real cement/clinker model has been trained or evaluated.
