# Minimum Industrial Cement Data Requirements

This document specifies the minimum data that must be collected before any real cement or clinker machine-learning project is considered legitimate.

Important constraints:

- This is a specification for future data collection, not a description of the current repository.
- The current repository does not satisfy these requirements.
- No synthetic target values, no formula-generated labels, and no fabricated plant measurements are allowed.
- Only measured experimental values may be treated as ground truth.

## 1. Objective

The goal is to produce a traceable industrial dataset that links:

raw material sample
→ raw mix / kiln feed
→ process time window
→ clinker sample
→ cement sample
→ laboratory result

This dataset must support defensible modeling of clinker quality, free CaO, and downstream cement properties using measured values, with proper temporal alignment and leakage control.

## 2. Required data chain

The minimum chain is:

1. raw material lots / samples
2. raw material chemical analysis
3. raw mix recipe and kiln-feed composition
4. kiln process conditions during the relevant production window
5. clinker sample(s) taken from the corresponding production interval
6. clinker XRF/XRD measurements
7. optional downstream cement sample(s)
8. cement quality tests and strength measurements

This chain must be linked by reliable identifiers and timestamps.

## 3. Data categories

### A. PLANT / EQUIPMENT METADATA

Required plant metadata for every dataset record or plant-operating period:

- plant_id
- line_id
- kiln_id
- kiln configuration
- preheater configuration
- precalciner configuration
- production capacity
- relevant equipment configuration
- start-up / shutdown status
- maintenance / downtime status
- raw mill configuration
- cooler configuration
- fuel system configuration
- control system / DCS version if relevant
- unit of measure conventions

Minimum descriptions:

- plant_id: unique plant identifier
- line_id: production line identifier
- kiln_id: unique kiln identifier
- kiln configuration: dry / wet / long kiln / suspension preheater / preheater-precalciner; design and operating configuration
- preheater/precalciner configuration: number of stages, cyclone configuration, tertiary air arrangement, calciner type, etc.
- production capacity: nominal tpd or tph and design basis
- relevant equipment configuration: raw mill, burner, cooler, fan arrangement, control scheme

These are not predictive variables by themselves, but they are required for traceability and contextual modeling.

### B. RAW MATERIAL DATA

For every raw material sample, the minimum required field set is:

- material_id
- material_type
- source / quarry / mine / supplier
- timestamp
- sample_id
- SiO2
- Al2O3
- Fe2O3
- CaO
- MgO
- SO3
- Na2O
- K2O
- Cl
- LOI
- moisture
- particle size / fineness where available
- relevant mineralogical information
- measurement method
- laboratory / instrument information
- analyst or lab identifier where available
- wet or dry basis indicator
- sampling location

Minimum requirements:

- Each measurement must specify the analytical basis: as-received, dry basis, ignited basis, or equivalent.
- Oxide analyses must be reported with units and method metadata.
- The material source and lot information must be traceable to the feed recipe.
- Mineralogical information may include XRD, microscopy, or qualitative mineralogy summary when available.

### C. RAW MIX / KILN FEED

Required for every production batch or feed interval:

- batch_id
- timestamp
- raw material proportions
- raw material lot IDs / material IDs
- kiln-feed chemistry
- LSF
- SM
- AM
- feed rate
- moisture
- fuel information relevant to feed preparation
- blend ratio metadata
- sample_id
- sampling location
- laboratory method

Minimum specification:

- Raw material proportion data must be recorded as actual mass or mass percentages from the blend design, not inferred from chemistry alone.
- Kiln-feed chemistry should include at least the same oxide set as the raw material chemistry, with clear basis information.
- LSF, SM, AM must be computed from measured oxide data and recorded with their formula definitions and basis.
- Feed rate and moisture must be time-stamped and traceable to the relevant process interval.

### D. PROCESS / KILN TELEMETRY

The dataset should include useful continuous or high-frequency process variables from the kiln and related systems. Minimum categories are:

- kiln temperatures
- preheater temperatures
- calciner temperature
- kiln pressure
- O2
- CO
- draft
- fuel flow
- fuel type / fuel properties
- kiln speed
- feed rate
- ID fan / relevant fan variables
- cooler operating variables
- other available DCS/SCADA variables

For every process variable, define:

- measurement name
- unit
- sampling frequency
- timestamp
- sensor/source
- expected role in modelling

Examples:

- kiln shell temperature, °C, 1-minute or 5-minute interval, timestamp from DCS, sensor ID, used as process-state proxy
- preheater top temperature, °C, 1-minute interval, sensor tag, used as thermal-stage indicator
- O2 in kiln exhaust, %, 1-minute interval, analyzer tag, used as combustion-control feature
- fuel flow, t/h or Nm3/h, 1-minute interval, fuel meter, used as thermal input feature
- cooler grate speed, rpm, 1-minute interval, PLC tag, used as cooling-rate feature

High-frequency variables are useful only if they are aligned to the correct production interval, not simply merged by nearest timestamp.

### E. CLINKER MEASUREMENTS

The clinker dataset must clearly separate measured and calculated values.

Preferred measured targets:

- Free CaO
- clinker oxide chemistry from XRF
- alite / C3S from XRD or Rietveld
- belite / C2S from XRD or Rietveld
- aluminate / C3A from XRD or Rietveld
- ferrite / C4AF from XRD or Rietveld
- minor phases where available

For every target, record:

- target name
- unit
- measurement method
- instrument
- sample location
- sample frequency
- sample_id
- timestamp
- laboratory / source
- basis / reporting method

Required label classification vocabulary:

- MEASURED_XRD
- MEASURED_RIETVELD
- MEASURED_XRF
- MEASURED_LAB
- BOGUE_CALCULATED
- CHEMISTRY_DERIVED
- SYNTHETIC

Only measured experimental values may be treated as ground truth.

Important rule:

- `BOGUE_CALCULATED` values are reference values and must be explicitly separated from measured mineralogical labels.
- `CHEMISTRY_DERIVED` quantities must not be treated as direct observed targets.
- `SYNTHETIC` values must never be used as ground truth.

### F. CEMENT QUALITY DATA

Define optional downstream targets such as:

- cement oxide chemistry
- fineness / Blaine
- setting time
- soundness
- mortar compressive strength
- other standardized quality measurements

Required fields:

- cement sample_id
- timestamp
- production / batch linkage
- test standard / method
- curing age where applicable
- sample location
- laboratory / source
- result unit
- instrument / method metadata
- associated clinker batch / production interval

Examples:

- cement oxide chemistry: XRF, wt%
- Blaine fineness: cm2/g
- setting time: min
- mortar compressive strength: MPa, at 1, 3, 7, 28 days

### G. TRACEABILITY / JOIN KEYS

The dataset must support a valid end-to-end chain:

raw material sample
→ raw mix / batch
→ kiln feed
→ process time window
→ clinker sample
→ cement sample
→ laboratory result

Minimum traceability fields:

- material_id
- source_id / quarry_id
- raw_material_sample_id
- raw_mix_batch_id
- kiln_feed_batch_id
- production_batch_id
- clinker_sample_id
- clinker_batch_id
- cement_sample_id
- cement_batch_id
- timestamp for every sampling or production interval
- plant_id
- line_id
- kiln_id
- sampling interval start and end
- product code / grade where applicable

Important rule:

Do not assume `batch_id` alone is sufficient unless the temporal relationship is also valid.

The dataset should explicitly record:

- sampling time
- production interval start/end
- feed entry time
- residence time window
- clinker sampling delay
- cement sampling delay

### H. TEMPORAL ALIGNMENT

Industrial process data must be aligned to the correct production and sampling interval.

Required time alignment concepts:

- process sensor frequency
- laboratory sampling frequency
- residence time
- feed-to-clinker delay
- clinker sampling delay
- cement sampling delay
- aggregation / windowing rules
- production shutdown periods

Minimum requirements:

- Every sensor measurement must have a timestamp.
- Every laboratory sample must have a sampling timestamp and result timestamp.
- The raw-material feed and kiln input interval must be known.
- For clinker and cement quality modeling, the process data must be aligned to the relevant production window, not simply matched by nearest timestamp.
- The delay between feed input and clinker output must be modeled explicitly.

This is a critical methodological requirement. Industrial clinker-quality studies commonly rely on synchronizing high-frequency process telemetry with lower-frequency XRF/XRD measurements and accounting for production residence time and delay.

### I. MINIMUM DATA VOLUMES

No universal magic number is appropriate for all plants. The required sample count depends on:

- number of predictors
- target variability
- number of plants / lines
- operating regimes
- sampling frequency
- missingness
- temporal dependence
- target distribution and noise

Recommended planning ranges:

1. Pilot dataset
   - minimum usable pilot for initial analytics and protocol validation
   - sufficient to establish data collection flow, linkage fidelity, and measurement method consistency
   - should include multiple operating conditions, not a single steady-state period

2. Useful research dataset
   - enough to support exploratory modeling and validation across a reasonable range of operating states
   - should include enough production intervals to capture major variation in feed chemistry and thermal conditions

3. Strong industrial dataset
   - enough to support robust multivariate modeling with proper validation and temporal splitting
   - should include multi-line or multi-period coverage and explicit validation by time or operating regime

The key point is that volume is secondary to traceability, measurement quality, and valid temporal alignment. A small but valid, measured dataset is more useful than a large but synthetic or weakly linked dataset.

### J. DATA QUALITY REQUIREMENTS

The data collection protocol must include automated and manual checks for:

- missing values
- duplicate records
- impossible values
- unit inconsistencies
- timestamp errors
- sensor failures
- laboratory outliers
- XRF / XRD consistency
- phase normalization
- batch linkage failures
- production shutdown periods
- sample contamination or identification errors

Specific checks:

- oxide totals must be reviewed against expected ranges
- chlorine or alkali values should be checked for outlier behavior
- free CaO must be checked against clinker chemistry and burn conditions
- XRF and XRD values must be reviewed for consistency with known phase chemistry and material balance
- sensor data should be flagged during maintenance or calibration intervals
- process data records should be filtered when production is not active
- all raw material and clinker sample IDs must be unique and verified

### K. LEAKAGE PREVENTION

Leakage protection is mandatory.

Variables that must not be used in an online predictive model when they are known only after the prediction point include:

- post-production clinker laboratory results
- future process measurements
- target-derived variables
- Bogue phases derived from target chemistry when predicting measured phases
- any future-corrected values that are unavailable at the time of prediction

Separate feature categories:

1. Online prediction features
   - feed chemistry known before or at production time
   - current process variables available within the same operating window
   - validated operational conditions available before the clinker sample is produced

2. Post-production diagnostic features
   - measured clinker chemistry
   - measured XRD mineralogy
   - lab results obtained after clinker production
   - analysis used for diagnosis, auditing, or calibration, not online prediction

The rule is simple:

- Features used for online control or prediction must be available at the prediction time.
- Diagnostic results obtained after production may be used later for analysis, model evaluation, or calibration, but not as online features for the same prediction event.

### L. FIRST REAL ML MODEL

The recommended first realistic target depends on the collected data and must be based on measured lab ground truth.

Candidate ranking:

1. Free CaO
   - required target measurement: measured free CaO from clinker lab analysis
   - minimum input: kiln feed chemistry, kiln process conditions, clinker chemistry, thermal history
   - advantages: direct quality metric, strong process relevance, often operationally important
   - limitations: must be measured by lab method, not Bogue-derived or formula-generated
   - leakage risks: severe if using post-production results as features or mixing future lab values into the feature set
   - validation requirements: temporal split, measured target only, proper alignment to clinker production window

2. Clinker phase prediction
   - required target measurement: measured phase fractions from XRD or Rietveld
   - minimum input: kiln feed chemistry, process telemetry, clinker oxide chemistry, burn conditions
   - advantages: directly tied to clinker mineralogy and product performance
   - limitations: requires reliable XRD/Rietveld measurements and proper phase normalization
   - leakage risks: high if Bogue phases are treated as labels, or if post-production XRD is used as a predictor of earlier production windows
   - validation requirements: measured phase labels and temporal validation by production interval

3. Clinker oxide prediction
   - required target measurement: measured XRF oxide chemistry for clinker
   - minimum input: raw mix, raw meal chemistry, kiln process state, fuel and burn conditions
   - advantages: more direct and often stable than phase prediction
   - limitations: still requires measured XRF values and tight process-time alignment
   - leakage risks: lower than phase prediction, but future lab results must still remain out of online features
   - validation requirements: aligned process window and proper laboratory quality control

4. Cement property prediction
   - required target measurement: measured cement chemistry, fineness, setting time, soundness, and/or mortar strength
   - minimum input: clinker chemistry, gypsum, fineness, process data, grinding conditions
   - advantages: directly linked to cement performance and final product quality
   - limitations: a larger dataset and strong plant-to-lab linkage are needed
   - leakage risks: high if using subsequent quality tests or post-mill data for online prediction when they are unavailable at the time
   - validation requirements: sample-based and batch-aware temporal validation

The first defensible model is usually the target with the fewest hidden assumptions and the most reliable ground-truth measurement. In a real clinker program, that often means measured Free CaO or measured clinker oxide chemistry before direct phase prediction, depending on data availability.

### M. FINAL DATA-ACQUISITION CHECKLIST

Use this checklist when exporting data from the plant and laboratory:

- required plant metadata available for each line and kiln
- unique plant_id, line_id, kiln_id
- raw material sample IDs and source information
- raw material oxide analyses with units and basis
- raw material moisture and fineness entries
- raw mix / kiln-feed proportions by batch
- kiln-feed chemistry and calculated LSF, SM, AM with formula definitions
- process telemetry with timestamps and sensor IDs
- fuel information with type, flow, and properties
- clinker sample IDs and timestamps
- measured clinker XRF data with method and instrument
- measured clinker phase values from XRD / Rietveld and their label classification
- measured free CaO with method and instrument metadata
- cement sample IDs and timestamps
- cement property test methods and curing ages
- linkage keys connecting feed → process window → clinker → cement
- documentation of residence time and delay correction
- evidence of missing-data and quality-control checks
- evidence that target values are measured, not Bogue-derived or synthetic

This checklist should be used before any ML training begins.

## 4. Final principle

A real cement/clinker ML project is only as strong as the validity of its labels and the reliability of its time alignment. The minimum requirement is not simply “more data”; it is a traceable, measured, time-aware industrial dataset with clear provenance, valid linkage, and defensible target definitions.
