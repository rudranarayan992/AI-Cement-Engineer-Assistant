# ML Readiness Assessment

This assessment is intentionally conservative. The goal is to identify which targets are realistically trainable with the available data and which are not.

## 1) Concrete compressive strength prediction

- Target: `Concrete compressive strength` or `Compressive Strength (MPa)`
- Dataset: `Concrete_Data.xls` (`Sheet1`)
- Usable samples: ~1030 rows in the main sheet
- Candidate features:
  - cement content
  - slag
  - fly ash
  - water
  - superplasticizer
  - coarse aggregate
  - fine aggregate
  - age
- Missingness: low / none in the main sheet
- Leakage risk: low to moderate
  - no time leakage obvious
  - no direct plant or batch leakage
  - but this is still a standardized benchmark dataset, not a production-stream dataset
- Recommended preprocessing:
  - remove duplicate rows
  - standardize numeric features
  - use train/validation split by randomized CV
  - check for nonlinearity and heteroscedasticity
- Recommended model: gradient boosting regressor or XGBoost / CatBoost regressor
- Recommended metrics: RMSE, MAE, R^2, possibly MAPE for reporting
- Engineering limitations: this is a recipe-based benchmark, not a process-control dataset; it does not represent kiln-to-cement production variation.

## 2) Slump / flow / 28-day strength prediction

- Target: `SLUMP(cm)`, `FLOW(cm)`, `Compressive Strength (28-day)(Mpa)`
- Dataset: `slump_test.data`
- Usable samples: 103 observations
- Candidate features:
  - cement, slag, fly ash, water, SP, coarse aggregate, fine aggregate
- Missingness: none
- Leakage risk: low
- Recommended preprocessing:
  - simple scaling
  - inspect for outliers and nonlinearity
- Recommended model: regression model such as random forest, gradient boosting, or elastic net baseline
- Recommended metrics: RMSE, R^2, MAE
- Engineering limitations: small sample size; output variables are workability and compressive strength for a concrete mix design dataset, not plant process data.

## 3) Blended concrete strength prediction

- Target: `Compressive Strength (MPa)`
- Dataset: `blended_cement_concrete_database.csv`
- Usable samples: 8,979 rows
- Candidate features:
  - cement, slag, fly ash, silica fume, calcined clay, limestone, water, superplasticizer, aggregates, age, curing temperature/humidity, specimen geometry
- Missingness: moderate to high in some columns
- Leakage risk: moderate
  - same DOI-derived studies may repeat mixtures or conditions
  - strong literature heterogeneity and possible publication-level leakage if split by publication is not respected
- Recommended preprocessing:
  - deduplicate by DOI + ingredient vector + age + specimen geometry
  - remove or flag records with missing essential features
  - stratify by DOI or publication if needed
- Recommended model: gradient boosting / tree ensembles with publication-level grouping in validation
- Recommended metrics: MAE, RMSE, R^2
- Engineering limitations: heterogeneous literature source; not a single operating context; lab conditions vary substantially.

## 4) Raw material chemistry / mix design inference

- Target: raw material clustering or blend proportion estimation
- Dataset: `Raw_Materials.xlsx`
- Usable samples: 6 rows only
- Candidate features: oxide composition and material type
- Missingness: moderate for some oxides
- Leakage risk: low but the dataset is too small for reliable ML training
- Recommended preprocessing: not yet recommended for model training; this dataset is better suited for rule-based characterization or material matching
- Recommended model: no robust ML recommendation at present
- Engineering limitations: too few observations and no time-series or batch variation

## 5) Free CaO prediction

- Target: free CaO %
- Dataset: none directly suitable
- Usable samples: 0 from the available raw datasets
- Candidate features: kiln chemistry, feed chemistry, temperature, raw meal fineness, combustion metrics
- Missingness: not available
- Leakage risk: high if constructed from derived metrics without a proper clinker record
- Recommended preprocessing: not feasible without a valid clinker dataset
- Recommended model: not recommended yet
- Engineering limitations: no direct clinker / free-CaO dataset is present

## 6) Clinker phase prediction (C3S/C2S/C3A/C4AF)

- Target: clinker phase fractions
- Dataset: none direct
- Usable samples: 0
- Candidate features: raw meal chemistry, kiln conditions, burnability proxies
- Missingness: absent
- Leakage risk: high if Bogue phases are treated as ground truth without lab confirmation
- Recommended preprocessing: not recommended yet
- Recommended model: not recommended yet
- Engineering limitations: target is not available as measured data; Bogue is derived rather than observed.

## Recommended first ML target

Best first ML target: concrete compressive strength from `Concrete_Data.xls` (`Sheet1`).

Why this is the best first target:

- larger sample size (~1030)
- direct target variable exists
- good feature matrix with standard concrete ingredients + age
- no obvious missingness
- strong engineering relevance
- low leakage risk relative to the other datasets
- no requirement for a latent clinker or kiln chain link

This is the cleanest first supervised-learning task available in the current data pool.
