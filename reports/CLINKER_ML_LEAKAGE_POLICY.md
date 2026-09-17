# CLINKER ML LEAKAGE POLICY

This policy defines the safe and unsafe variable families for future clinker-model work. It is a scientific control document, not a training plan.

## SAFE

These are legitimate upstream or process variables if properly time-anchored and separated from the target:

- raw-material chemistry
- raw-mix proportions
- kiln feed composition
- legitimate pre-clinker process variables
- measured process variables whose timing is clearly upstream of clinker sampling

## CONDITIONAL

These may be usable only with explicit time-window logic and scientific justification:

- variables measured near the clinker sampling point
- delayed process measurements
- process indicators that occur within a defined production window but may still carry lag

## HIGH RISK

These should be treated as leakage-prone when the objective is prediction of clinker chemistry or phases:

- post-production clinker chemistry when predicting clinker chemistry
- measured clinker phases when predicting phases
- Free CaO when predicting Free CaO
- Bogue phase calculations derived from the same oxide inputs as the target
- any target-derived feature built from the same sample’s target or from the same lab measurement stream

## Temporal leakage rule

A future model must not use data from the same production cycle, same sample, or same measurement window in a way that leaks target information into the input space.

The system must enforce a clear temporal boundary:

- upstream process variables may be safe if they precede the clinker production and sampling window
- target-adjacent variables are conditional and must be justified
- same-sample clinker chemistry or measured phase fractions are not valid predictors for themselves or for derived labels

## Bogue-specific rule

Bogue-calculated C3S/C2S/C3A/C4AF are reference values only. They may be used for benchmarking, comparison, or as feature candidates only when the scientific protocol explicitly excludes direct target leakage. They are not acceptable as measured phase labels for a future clinker model.
