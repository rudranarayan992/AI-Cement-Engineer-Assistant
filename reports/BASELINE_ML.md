# Baseline Machine Learning Report

## Dataset

- Source: `Concrete_Data.xls`
- Sheet: `Sheet1`
- Raw source location: `c:\Users\rudra\Desktop\civil-project\` (parent directory, preserved unchanged)
- Initial shape: 1030 rows × 9 columns
- Duplicate rows removed: 25 exact duplicates
- Final shape: 1005 rows × 9 columns

## Features

All features are in units of kg/m³ or day:

1. `cement` (kg/m³)
2. `slag` (kg/m³) - Blast Furnace Slag
3. `fly_ash` (kg/m³)
4. `water` (kg/m³)
5. `superplasticizer` (kg/m³)
6. `coarse_aggregate` (kg/m³)
7. `fine_aggregate` (kg/m³)
8. `age` (day)

## Target

- `compressive_strength` (MPa - megapascals)
- Range: [2.33, 82.60] MPa

## Preprocessing

1. **Schema validation**: Verify expected columns and rename to canonical names
2. **Duplicate removal**: Drop exact duplicate rows before splitting
3. **Type coercion**: Convert all features and target to numeric (reject failures)
4. **Missing values**: No missing values in the concrete dataset
5. **Train/test split**: 80/20 split using `train_test_split` with `random_state=42` and `shuffle=True`
6. **Imputation**: Fit `SimpleImputer(strategy='median')` on training data only, apply to both train and test
7. **Scaling**: Fit `StandardScaler` on training data only for Ridge and SVR; Random Forest and XGBoost do not use scaling

## Train/test split

- **Training set**: 804 samples
- **Test set**: 201 samples
- **Ratio**: 80/20
- **Random seed**: 42
- **Shuffle**: True
- **No target leakage**: Target excluded from feature matrix; indices disjoint

## Cross-validation

- **Method**: 5-fold KFold
- **Shuffle**: True
- **Random seed**: 42 (consistent across all models)
- **Only on training set**: CV folds use only the 804-sample training data; test set held completely out

## Models

### 1. Ridge Regression

- **Library**: scikit-learn
- **Hyperparameters**: `alpha=1.0`
- **Preprocessing**: median imputer + StandardScaler
- **Reason**: Linear baseline with L2 regularization

### 2. Random Forest Regressor

- **Library**: scikit-learn
- **Hyperparameters**: `n_estimators=300`, `random_state=42`, `n_jobs=-1`
- **Preprocessing**: median imputer only (tree-based, no scaling needed)
- **Reason**: Non-linear ensemble; robust to feature scales

### 3. Support Vector Regression (SVR)

- **Library**: scikit-learn
- **Hyperparameters**: `kernel='rbf'`, `C=10.0`, `epsilon=0.1`, `gamma='scale'`
- **Preprocessing**: median imputer + StandardScaler
- **Reason**: Non-linear with explicit regularization; requires scaling

### 4. XGBoost Regressor

- **Library**: xgboost (installed in project environment)
- **Hyperparameters**:
  - `objective='reg:squarederror'`
  - `n_estimators=500`
  - `max_depth=6`
  - `learning_rate=0.05`
  - `subsample=0.9`
  - `colsample_bytree=0.9`
  - `random_state=42`
  - `n_jobs=-1`
  - `verbosity=0`
- **Preprocessing**: median imputer only (gradient boosting, native feature scaling)
- **Reason**: Modern gradient boosting; often top performer on tabular data

## Hyperparameters

All hyperparameters were set conservatively to reflect a first baseline experiment:

- No intensive grid search or Bayesian optimization
- No tuning on the test set
- Parameters chosen for general robustness and reasonable computational cost

## CV Results

| Model | CV MAE Mean | CV MAE Std | CV RMSE Mean | CV RMSE Std | CV R² Mean | CV R² Std |
|---|---:|---:|---:|---:|---:|---:|
| Ridge | 8.109 | 0.068 | 10.203 | 0.152 | 0.589 | 0.029 |
| Random Forest | 3.872 | 0.265 | 5.351 | 0.479 | 0.886 | 0.022 |
| SVR | 5.336 | 0.151 | 7.254 | 0.256 | 0.793 | 0.010 |
| XGBoost | 3.129 | 0.196 | 4.626 | 0.500 | 0.915 | 0.019 |

**Best by CV R²:** XGBoost (0.915 mean)

## Test-set results

| Model | Test MAE | Test RMSE | Test R² |
|---|---:|---:|---:|
| Ridge | 8.898 | 11.194 | 0.580 |
| Random Forest | 3.462 | 5.120 | 0.912 |
| SVR | 5.452 | 7.692 | 0.802 |
| XGBoost | 2.459 | 4.069 | 0.944 |

**Best by test R²:** XGBoost (0.944)

## Best baseline model

**XGBoost Regressor**

- Cross-validation R²: 0.915 ± 0.019
- Test R²: 0.944
- Test MAE: 2.46 MPa
- Test RMSE: 4.07 MPa

This model demonstrates strong generalization on both the CV and test sets, with the lowest test error among all baselines.

## Limitations

### Critical scientific disclaimer

**This is a benchmark regression on a concrete mix design dataset used to validate the project's ML infrastructure. It should NOT be interpreted as suitable for industrial cement manufacturing.**

- The dataset is a published benchmark of concrete recipes, not a plant-scale production dataset
- It captures laboratory or controlled environment compressive strength testing, not real-world variations
- The features are concrete mix proportions, not raw-material chemistry, kiln conditions, or clinker quality
- This model cannot replace engineering expertise or process control in industrial operations

### Research direction

The project's long-term research path is:

Raw Materials → Raw Mix → Raw Meal Chemistry → LSF/SM/AM → Kiln Conditions → Clinker Quality → Cement Quality → Concrete Strength

The concrete dataset is only the first controlled ML checkpoint to validate the baseline infrastructure.

### Model limitations

- Ridge Regression performed poorly (R² 0.58), indicating the relationship is non-linear
- Tree-based models (RF, XGBoost) capture the non-linearity well but may not generalize to significantly different concrete recipes
- SVR is intermediate; kernel choice and hyperparameters could be tuned further
- No feature importance or interpretability analysis is included at this stage
- No SHAP, PIML, or explainability layers have been implemented

## Reproducibility information

- **Random seed**: 42 (used consistently in train/test split and all CV operations)
- **Test set**: Held completely separate; used only for final evaluation
- **CV strategy**: 5-fold KFold with shuffle=True and random_state=42
- **Preprocessing**: Fit only on training data, applied to test data
- **Software versions**:
  - Python: 3.14.0
  - scikit-learn: 1.9.0
  - pandas: 3.0.5
  - joblib: 1.6.0
  - xgboost: (installed)

Running this pipeline again with the same seed and data will produce identical model artifacts and metrics (within numerical precision limits).

## Files created

- `models/baseline/ridge_model.joblib`
- `models/baseline/ridge_model.json` (metadata)
- `models/baseline/random_forest_model.joblib`
- `models/baseline/random_forest_model.json` (metadata)
- `models/baseline/svr_model.joblib`
- `models/baseline/svr_model.json` (metadata)
- `models/baseline/xgboost_model.joblib`
- `models/baseline/xgboost_model.json` (metadata)
- `reports/baseline_model_results.csv` (summary table)
- `reports/BASELINE_ML.md` (this report)
