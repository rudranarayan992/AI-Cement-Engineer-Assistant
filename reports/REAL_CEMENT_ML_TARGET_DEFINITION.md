# Real Cement ML Target Definition

This document defines the structural requirements for real cement and clinker model targets before any supervised-learning work begins.

The purpose is to define what is legitimate ground truth and how it must be collected and labeled.

## 1. Rule: only measured values are valid targets

For any target, the following rule applies:

- `MEASURED_XRD`
- `MEASURED_RIETVELD`
- `MEASURED_XRF`
- `MEASURED_LAB`

These are the only acceptable ground-truth labels for supervised learning.

The following values must not be used as model targets without explicit scientific justification and proper separate treatment:

- `BOGUE_CALCULATED`
- `CHEMISTRY_DERIVED`
- `SYNTHETIC`

In particular:

- Bogue phase values are not measured clinker mineralogy.
- chemistry-derived predictions are not experimental ground truth.
- synthetic labels are not acceptable in a real industrial model.

## 2. Required target structure

Every valid target must be defined with:

- target name
- unit
- measurement method
- instrument
- sample location
- sample frequency
- sample_id
- timestamp
- laboratory source
- label class
- production context / batch linkage

A target record is not valid if it lacks a measured method and traceability to a sample or production interval.

## 3. Target definitions

### 3.1 Free CaO

Definition:

- concentration of free calcium oxide in clinker, typically reported as wt%.

Minimum required measurement:

- measured clinker free CaO via laboratory method

Required metadata:

- sample_id
- timestamp
- clinker_sample_id
- plant_id / line_id / kiln_id
- instrument and lab method
- measurement_label = MEASURED_LAB

Notes:

- A free CaO value generated from a process model or from Bogue-type formula is not a measured target.
- It may be used as a diagnostic or reference quantity only if clearly labeled.

### 3.2 Clinker phase fractions

Target candidates:

- alite / C3S
- belite / C2S
- aluminate / C3A
- ferrite / C4AF
- minor phases where available

Minimum required measurement:

- XRD or Rietveld analysis of clinker sample

Required metadata:

- target_name
- unit (% mass)
- measurement_method = XRD or Rietveld
- instrument name
- lab source
- sample_id
- timestamp
- clinker sample location
- measurement_label = MEASURED_XRD or MEASURED_RIETVELD

Important rule:

- A Bogue value is not a valid XRD target even if it is numerically plausible.
- Bogue values may be used as a reference or benchmark, but not as the target label for a measured mineralogical model.

### 3.3 Clinker oxide chemistry

Target candidates:

- CaO
- SiO2
- Al2O3
- Fe2O3
- MgO
- SO3
- Na2O
- K2O
- Mn2O3 or other relevant oxides

Minimum required measurement:

- XRF or equivalent measured chemistry on clinker sample

Required metadata:

- measurement_label = MEASURED_XRF
- oxide basis (dry basis / ignited basis if applicable)
- sample_id
- lab and instrument

### 3.4 Cement quality targets

Examples:

- cement oxide chemistry
- Blaine fineness
- setting time
- soundness
- standard mortar compressive strength at specified ages

Minimum required measurement:

- lab test according to relevant standard

Required metadata:

- cement_sample_id
- timestamp
- batch linkage
- curing age if applicable
- measurement standard / method
- instrument
- measurement_label = MEASURED_LAB

## 4. Target labeling taxonomy

Each target must be assigned exactly one of the following classes:

- MEASURED_XRD: measured by X-ray diffraction
- MEASURED_RIETVELD: measured by Rietveld refinement
- MEASURED_XRF: measured by X-ray fluorescence
- MEASURED_LAB: measured by wet chemistry or lab analysis
- BOGUE_CALCULATED: calculated from chemistry, not directly measured
- CHEMISTRY_DERIVED: derived by formula or mass balance, not directly measured
- SYNTHETIC: generated or fabricated, not valid for real ground truth

Only the first four classes may be treated as ground truth for modeling.

## 5. Required target metadata

For every target, the dataset must provide:

- target_name
- unit
- target_value
- measurement_method
- instrument
- sample_id
- timestamp
- sample location
- bias / correction note if applicable
- laboratory or source
- batch / production linkage
- target_class

Without this metadata, the target is not auditable and must not be used in a supervised-learning project.

## 6. Target priority for a real industrial program

The most defensible first targets are the ones with the strongest measurement provenance and clearest operational relevance.

Ranked order:

1. Free CaO
   - first if measured clinker free CaO is available and linked to kiln process windows
2. clinker phase prediction
   - only if measured XRD / Rietveld values exist
3. clinker oxide prediction
   - valid if measured XRF chemistry is available
4. cement property prediction
   - valid if measured cement tests are available and time-linked to clinker and production conditions

This ranking should be treated as a data-availability priority, not as a claim that the current repository provides those measurements.

## 7. What is not acceptable

The following are not acceptable as final targets in a real dataset:

- values generated in a Python script from formulae
- Bogue phases used as if they are measured phase fractions
- calculated free CaO values used as real lab measurements
- synthetic production data generated to mimic kiln behavior
- inferred labels without a measurement protocol
- target values not tied to a real sample and timestamp

These should be recorded as diagnostic references or model-usage placeholders only, not as ground truth.

## 8. Validation requirements before training

Before any training begins, confirm all of the following:

- each target value is associated with a real sample
- each target has a measurement method and instrument
- each target is time-stamped
- each target is linked to the appropriate production interval
- each target is classified as measured or derived
- Bogue and chemistry-derived values are kept separate from measured targets
- the data split respects time and production dependence
- no future or post-production measurements are used as online predictors

## 9. Final definition of a legitimate clinker target

A legitimate target must satisfy all of the following:

- It is measured on a real clinker or cement sample.
- It has a sample_id and timestamp.
- It is performed by a recognized method and instrument.
- It is traceable to the correct production batch / process window.
- It is clearly classified under the allowed measured-target taxonomy.
- It is not a synthetic or formula-derived value.

If any of these conditions fail, the target is not a valid industrial ground-truth label.

## 10. Practical recommendation

For an initial real industrial project, the strongest first objective is usually one of the following:

- measured free CaO prediction from kiln and feed data
- measured clinker oxide prediction from feed and process data
- measured XRD phase prediction only after a fully measured phase dataset exists

The first model should be selected based on the existence of measured labels, not model ambition.

The current repository does not satisfy these requirements and should not be described as a measured industrial dataset.
