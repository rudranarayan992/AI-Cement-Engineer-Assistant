# AI Cement Engineer

## Project definition
AI Cement Engineer is a hybrid engineering decision-support system for cement and concrete performance. It is not a single monolithic ML model. It is a staged, physics-informed, explainable, and case-aware system that combines:

- deterministic engineering calculations
- multi-stage ML models at the correct process boundaries
- historical case memory and retrieval
- uncertainty and OOD monitoring
- XAI / SHAP explanation
- engineering constraints and standards checks
- actual lab-result feedback and controlled retraining

The system is designed around the principle that the LLM is not a replacement for numerical models. The LLM receives calculations, predictions, historical cases, uncertainty, XAI, and constraints, and then produces a grounded engineering recommendation for human approval.

## Academic framing
AI Cement Engineer: A Hybrid Physics-Informed, Explainable Machine-Learning and Historical-Memory Decision Support System for Cement and Concrete Performance

## Core pipeline
RAW MATERIALS
  ↓
CHEMISTRY
  ↓
MASS BALANCE
  ↓
RAW MIX / RAW MEAL
  ↓
LSF / SM / AM
  ↓
KILN / PROCESS
  ↓
CLINKER
  ↓
C3S / C2S / C3A / C4AF / FREE CAO
  ↓
CEMENT BLENDING
  ↓
GYPSUM / SCM / GRINDING
  ↓
CEMENT QUALITY
  ↓
CONCRETE MIX
  ↓
CURING
  ↓
3 / 7 / 14 / 21 / 28 / 56 / 90 DAY
  ↓
PERFORMANCE
  ↓
FAILURE DETECTION
  ↓
LIKELY CONTRIBUTING FACTORS
  ↓
HISTORICAL EVIDENCE
  ↓
SHAP + UNCERTAINTY
  ↓
ENGINEERING RECOMMENDATION
  ↓
ACTUAL LAB RESULT
  ↓
ERROR
  ↓
MODEL MONITORING
  ↓
CONTROLLED RETRAINING

## System principle
Do not build one giant ML model that tries to learn the whole cement-to-concrete chain. Instead, use a multi-stage hybrid architecture.

### Stage 1 — Raw materials
Inputs include limestone, clay/shale, laterite, iron corrective, gypsum, fly ash, slag, calcined clay, and other SCMs. For each material, the system tracks CaO, SiO2, Al2O3, Fe2O3, MgO, SO3, Na2O, K2O, LOI, moisture, source, batch, date, and sample ID.

### Stage 2 — Engineering calculations
Use established equations for:
- mass balance
- moisture correction
- weighted chemistry
- LSF
- SM
- AM
- raw-meal chemistry
- blending

This is deterministic engineering, not ML.

### Stage 3 — Clinker prediction
ML becomes useful only where a real measured target exists. Candidates include:
- raw-meal chemistry
- LSF / SM / AM
- kiln feed
- kiln temperatures
- fuel and O2
- CO
- feed rate and residence/process variables
- cooling conditions

Targets can include free CaO, C3S, C2S, C3A, C4AF, and clinker quality indicators, but only after validated measured plant data are available.

### Stage 4 — Cement quality model
The next stage combines clinker, gypsum, SCMs, grinding, and process variables to predict cement properties such as fineness, SO3, setting time, soundness, and strength at multiple ages.

### Stage 5 — Concrete model
Concrete modeling uses cement properties, clinker phases, SCM, water, aggregate, admixture, w/b, curing, and age to predict strength and performance across multiple ages.

## Architectural rule for the LLM
The LLM is an advisory layer to the engineered system. It does not replace numerical models. It receives:
- engineering calculations
- model predictions
- historical cases
- uncertainty and OOD status
- XAI / SHAP explanations
- constraints and standards rules

Then it produces a recommendation that must be reviewed by an engineer before action.

## 17-module architecture
1. AI Command Center
2. Raw Materials
3. Raw Mix / Raw Meal
4. Kiln / Process
5. Clinker
6. Cement Blending
7. Cement Quality
8. Concrete Mix
9. Multi-Age Strength
10. Failure Detection
11. Likely Contributing Factors
12. Historical Memory
13. XAI / SHAP
14. Uncertainty / OOD
15. What-If / Optimization
16. Actual vs Predicted
17. Model Center / Retraining

## Multi-age strength logic
The strength engine should use a multi-age model rather than separate isolated single-age models. The project target structure is:
- 3d
- 7d
- 14d
- 21d
- 28d
- 56d
- 90d

The system should validate whether the predicted strength curve is physically sensible, and it should flag implausible monotonicity or non-physical behavior.

## Failure and root-cause logic
A low 28-day strength should trigger investigation across the full chain:
- raw material
- clinker chemistry
- C3S / Free CaO
- fineness
- SO3
- SCM
- water/binder ratio
- curing
- aggregate and mix design

This is not an unqualified causal claim. The system should describe these as likely contributing factors supported by model output, process knowledge, and historical evidence.

## Historical memory
The project includes a learning loop from new cases to actual lab results, error analysis, validation, and retraining. Historical records are essential for:
- similar case retrieval
- based-on-measured-history recommendations
- process condition comparison
- prior failure review
- model improvement candidates

## Model acceptance criteria
The project should not promise vague accuracy claims. Instead, it should define target-specific acceptance metrics such as:
- C3S: MAE / RMSE / MAPE / R²
- Free CaO: MAE / RMSE / bias
- Blaine: MAE / RMSE
- Setting time: MAE / interval coverage
- 3d / 7d / 28d / 90d strength: MAE / RMSE / R²

## Validation workflow
NEW CASE
  ↓
Historical search
  ↓
Prediction
  ↓
Recommendation
  ↓
CASE SAVED
  ↓
Actual lab result
  ↓
Actual vs predicted
  ↓
Error
  ↓
Validated case
  ↓
Historical memory
  ↓
Training candidate
  ↓
Candidate model
  ↓
Validation
  ↓
Compare against production model
  ↓
Engineer approval
  ↓
New model

## Quick start
```bash
cd AI_Cement_Project
streamlit run app/streamlit_app.py
python train_all_models.py
python -m pytest -q
```

## Scientific boundary
The repository supports chemistry-aware raw-material and raw-mix engineering, and it includes downstream concrete benchmarking where valid measured data exist. Clinker-phase ML remains intentionally blocked until a real, traceable, measured clinker target dataset is accepted and validated.

The system therefore follows a safe hybrid approach: deterministic calculations first, ML only in the right domain, explainable diagnostics, engineering memory, uncertainty-aware recommendations, and controlled retraining after lab validation.

