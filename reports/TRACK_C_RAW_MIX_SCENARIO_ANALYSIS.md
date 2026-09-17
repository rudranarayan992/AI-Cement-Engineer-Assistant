# Track C: Raw-Mix Scenario Analysis

## 1. Data source

This scenario analysis uses the repository's legitimate raw-material assay table:

- `data/raw_materials/raw_materials_database.csv`

The inputs are treated as measured material assay values. The downstream raw-mix outputs are treated as calculated engineering outputs only.

## 2. Raw-material inputs

The analysis uses the repository raw-materials dataset with the following materials:

- `LS_001` limestone
- `CLAY_001` clay/shale
- `SAND_001` silica sand
- `IRON_001` iron ore

Required chemistry for each material includes:

- CaO
- SiO2
- Al2O3
- Fe2O3
- MgO
- SO3
- LOI

No missing chemistry is silently filled with zero. Invalid or missing oxide values are reported as errors.

## 3. Calculation method

The raw-mix scenario engine performs deterministic weighted oxide calculations using the same chemistry convention used in the project raw-mix utilities:

- weighted oxide composition of the recipe
- proportion normalization to 100%
- optional basis conversion when requested
- LSF, SM, and AM appraisal from the calculated oxide composition

The calculation is deterministic and traceable; it is not a machine-learning model.

## 4. Baseline result

Baseline recipe used for the valid engineering example:

- `LS_001 = 78.0%`
- `CLAY_001 = 14.0%`
- `SAND_001 = 5.0%`
- `IRON_001 = 3.0%`

Validated result from the raw-mix scenario engine:

- LSF = 87.05
- SM = 2.086
- AM = 0.902

This reproduces the accepted Track C baseline values and stays inside the chemistry-only scope.

## 5. Scenario analysis

The scenario engine accepts a baseline recipe and a candidate recipe, then compares them directly by absolute and percentage-point change for:

- CaO
- SiO2
- Al2O3
- Fe2O3
- MgO
- LSF
- SM
- AM

This is a deterministic engineering comparison only. It does not infer clinker quality.

## 6. Sensitivity analysis

The module supports deterministic one-factor-at-a-time sensitivity analysis.

For each raw-material, the scenario engine:

1. increases or decreases that material by a configured increment
2. rebalances the remaining materials to preserve 100%
3. recomputes chemistry and moduli
4. reports the resulting changes in LSF, SM, AM, CaO, SiO2, Al2O3, and Fe2O3

This is labeled explicitly as:

DETERMINISTIC CHEMISTRY SENSITIVITY

It is not causal ML and not a clinker optimization model.

## 7. Engineering constraints

The engine accepts plant-specific windows such as:

- `LSF_min`, `LSF_max`
- `SM_min`, `SM_max`
- `AM_min`, `AM_max`

Each scenario is evaluated as:

- PASS
- WARNING
- FAIL

Plant-specific limits are configuration inputs, not universal scientific constants.

## 8. Limitations

This module does NOT predict clinker quality.

This module does NOT prove that a particular raw mix will produce a specific C3S, C2S, C3A, C4AF, or Free CaO value.

It only calculates and compares engineered raw-meal chemistry states derived from measured material assays. Any future clinker prediction work requires a measured, traceable clinker dataset and separate scientific validation.
