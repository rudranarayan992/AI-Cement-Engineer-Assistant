# Concrete Baseline Preprocessing Pipeline

## Source dataset

- Source file: `Concrete_Data.xls`
- Location: project sibling directory (preserved as original raw data)
- Sheet used: `Sheet1`
- Raw datasource remains unchanged.

## Features

The canonical feature set for the baseline regression task is:

- `cement`
- `slag`
- `fly_ash`
- `water`
- `superplasticizer`
- `coarse_aggregate`
- `fine_aggregate`
- `age`

These are mapped from the original workbook column names, which include units and descriptive labels such as:

- `Cement (component 1)(kg in a m^3 mixture)`
- `Blast Furnace Slag (component 2)(kg in a m^3 mixture)`
- `Fly Ash (component 3)(kg in a m^3 mixture)`
- `Water  (component 4)(kg in a m^3 mixture)`
- `Superplasticizer (component 5)(kg in a m^3 mixture)`
- `Coarse Aggregate  (component 6)(kg in a m^3 mixture)`
- `Fine Aggregate (component 7)(kg in a m^3 mixture)`
- `Age (day)`

## Target

- `compressive_strength`
- Units: MPa (megapascals)
- Original raw column: `Concrete compressive strength(MPa, megapascals) `

## Units and raw data profile

- Cement, slag, fly ash, water, superplasticizer, coarse aggregate, fine aggregate: kg/m^3 mixture
- Age: days
- Compressive strength: MPa
- Dataset shape: 1030 rows x 9 columns
- Missing values: 0 in the raw dataset
- Duplicate rows: 25 exact duplicates
- Negative values: none
- Impossible values: none in the raw sheet; zero values are valid for slag, fly ash, and superplasticizer when those ingredients are absent in a given mixture.
- Data types: all numerical columns are float or integer values after conversion.

## Cleaning decisions

1. Preserve the original raw workbook untouched.
2. Read the raw Excel file deterministically with `pd.read_excel(..., sheet_name='Sheet1')`.
3. Validate that the expected schema is present.
4. Rename the raw Excel columns to canonical names for consistent downstream processing.
5. Convert all feature and target columns to numeric values using `pd.to_numeric(..., errors='raise')`.
6. Drop exact duplicate rows before splitting.
7. Keep any missing values in the raw data for handling in the training-only imputer.
8. Reject negative feature values because they are not physically valid for the concrete mix design table.
9. Reject missing target values because the supervised regression target must be available for every labeled example.

## Missing-value policy

- Missing values are not filled before train/test splitting.
- The missing-value imputer is fit only on the training set using the median strategy.
- The same fitted imputer is then applied to the held-out test set.
- This prevents target and feature leakage from the test set into the preprocessing stage.

## Split strategy

- Split type: train/test split for regression
- Test size: 20%
- Random seed: 42
- Shuffle: enabled
- Function: `train_test_split(..., test_size=0.2, random_state=42, shuffle=True)`

This is deterministic and reproducible.

## Leakage prevention

The pipeline follows the required rule:

- No scaler, imputer, or transformation that learns statistics from the dataset may be fit before splitting.
- Each transformer is fit only on the training split.
- The fitted transformer is then applied to the test split.
- The target is never included in the feature matrix.
- The raw dataset remains unchanged and is never overwritten.

## Output data location

Processed train/test feature and label files are saved under:

- `data/processed/`

Files created:

- `concrete_X_train.csv`
- `concrete_X_test.csv`
- `concrete_y_train.csv`
- `concrete_y_test.csv`

## Limitations

- This is a benchmark concrete recipe dataset, not a plant-level production dataset.
- It is not a full cement production chain dataset and should not be interpreted as such.
- The pipeline is only for the first baseline target: concrete compressive strength prediction.
- No model training, hyperparameter tuning, optimization, or PIML layers are included in this Step 7 work.
