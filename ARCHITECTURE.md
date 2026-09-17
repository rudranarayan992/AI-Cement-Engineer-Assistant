# AI Cement Engineer Architecture

## Hybrid engineering system definition

The project is defined as a hybrid engineering system rather than a single monolithic ML model.

AI CEMENT ENGINEER
  │
  ┌──────────────────┼──────────────────┐
  ▼                  ▼                  ▼
ENGINEERING         ML               MEMORY
CALCULATIONS       PREDICTIONS      + CASES
  │                  │                  │
  └──────────────────┼──────────────────┘
                     ▼
              DIAGNOSTICS
                     │
                     ▼
               UNCERTAINTY
                     │
                     ▼
                     XAI
                     │
                     ▼
             RECOMMENDATION
                     │
                     ▼
                     LLM
                     │
                     ▼
           ENGINEER APPROVAL
                     │
                     ▼
              ACTUAL LAB DATA
                     │
                     ▼
            MODEL MONITORING
                     │
                     ▼
            CONTROLLED RETRAINING

Important rule: the LLM does not replace the numerical models. It receives engineering calculations, predictions, historical cases, uncertainty, XAI outputs, and operating constraints, and then produces a recommendation for engineer review.

## Multi-stage architecture

### Stage 1 — Raw materials
Inputs:
- Limestone
- Clay / shale
- Laterite
- Iron corrective
- Gypsum
- Fly ash
- Slag
- Calcined clay
- Other SCMs

For each material, track:
- CaO
- SiO2
- Al2O3
- Fe2O3
- MgO
- SO3
- Na2O
- K2O
- LOI
- Moisture
- source
- batch
- date
- sample ID

### Stage 2 — Engineering calculations
Apply established equations before ML:
- mass balance
- moisture correction
- weighted chemistry
- LSF
- SM
- AM
- raw meal chemistry
- blending

This stage is deterministic and should not be delegated to a generic ML model.

### Stage 3 — Clinker prediction
ML becomes useful only at this boundary.

Potential inputs:
- raw-meal chemistry
- LSF / SM / AM
- kiln feed
- kiln temperatures
- fuel
- O2
- CO
- feed rate
- residence or process variables
- cooling conditions

Potential targets:
- Free CaO
- C3S
- C2S
- C3A
- C4AF
- clinker quality indicators

This step should be supported by measured industrial plant data and validated gauges, not by synthetic or Bogue-only proxies.

### Stage 4 — Cement quality model
After clinker, combine:
- clinker
- gypsum
- slag
- fly ash
- calcined clay
- grinding and process variables

Targets may include:
- Blaine / fineness
- SO3
- setting time
- soundness
- 3-day strength
- 7-day strength
- 28-day strength
- other measured properties

### Stage 5 — Concrete performance
Cement becomes an input into the concrete model.

Inputs include:
- cement properties
- cement chemistry
- clinker phases
- SCM
- water
- aggregate
- admixture
- w/b
- curing
- age

Targets and outputs:
- 3d
- 7d
- 14d
- 21d
- 28d
- 56d
- 90d

The concrete strength engine should be a multi-age model rather than five disconnected single-age models.

## Strength logic

The multi-age strength architecture should be:

MATERIAL
  +
MIX DESIGN
  +
CURING
  +
AGE
  ↓
MULTI-AGE MODEL
  ↓
  ┌──────────────┼──────────────┐
  ↓              ↓              ↓
 3d             7d             14d
  ↓              ↓              ↓
 21d            28d             56d
                 ↓
                90d

The system must check whether the predicted strength curve is physically plausible before accepting it. A sequence like 3d > 7d > 14d > 28d without appropriate behavior should be flagged as an engineering warning.

## Failure detection and likely contributing factors
Failure logic should investigate the full chain rather than issue a simplistic low-strength verdict.

Example:
28-day strength LOW
  │
  ├── Raw material?
  │
  ├── Clinker?
  │
  ├── C3S?
  │
  ├── Free CaO?
  │
  ├── Fineness?
  │
  ├── SO3?
  │
  ├── SCM?
  │
  ├── w/b?
  │
  ├── curing?
  │
  └── aggregate / mix?

This is the purpose of failure detection and likely-contributing-factors analysis.

## Important caution on causality
SHAP tells us which features contributed strongly to a prediction. It does not prove physical causation.

Therefore, the UI and guidance should say:
- Likely contributing factor
rather than:
- Confirmed root cause

unless the conclusion is supported by lab evidence, historical case review, or process knowledge.

## Historical memory
The architecture explicitly includes:

CURRENT CASE
  ↓
HISTORICAL DATABASE
  ↓
EXACT / CLOSE CASES
  +
SIMILAR CASES
  ↓
PREVIOUS LAB RESULTS
PREVIOUS PROCESS CONDITIONS
PREVIOUS FAILURES
PREVIOUS RECOMMENDATIONS

This allows engineers to ask questions such as:
- Have we produced cement with similar clinker chemistry?
- What happened in similar cases?
- What were the measured strengths and process conditions?

This creates engineering memory rather than a black-box model.

## Learning loop
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

This is the essential feedback loop of the system.

## Model validation and metrics
The project should not claim broad accuracy percentages without target-specific validation. Use acceptance criteria per target, such as:

TARGET               METRICS
────────────────────────────────────
C3S                  MAE / RMSE / MAPE / R²
Free CaO             MAE / RMSE / bias
Blaine               MAE / RMSE
Setting time         MAE / interval coverage
3d strength          MAE / RMSE / R²
7d strength          MAE / RMSE / R²
28d strength         MAE / RMSE / R²
90d strength         MAE / RMSE / R²

The dashboard should report measured model quality in this form:
MODEL VALIDATION

28-day strength
R²       0.91
MAE      3.5 MPa
RMSE     5.1 MPa
N        201
Status: VALIDATED ON HOLDOUT DATA

## 17 modules
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

## Full flow
RAW MATERIAL
  ↓
CHEMISTRY
  ↓
MASS BALANCE
  ↓
RAW MIX
  ↓
LSF / SM / AM
  ↓
KILN / PROCESS
  ↓
CLINKER
  ↓
C3S / C2S / C3A / C4AF / Free CaO
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

## Practical system rule
The project should be implemented as a hybrid engineering system with this explicit order:

1. compute chemistry and process metrics
2. model only where real measured labels exist
3. apply engineering and standards checks
4. run XAI and uncertainty analysis
5. retrieve similar historical cases
6. generate engineering recommendations
7. require engineer approval
8. store actual lab outcomes
9. monitor and retrain under controlled conditions

This is the design that best matches the intended project.
