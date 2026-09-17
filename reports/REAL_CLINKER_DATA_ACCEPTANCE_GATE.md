# Real Clinker Data Acceptance Gate

## Purpose

This approval gate defines whether a candidate clinker dataset is scientifically usable for research. The dataset may pass only if the required evidence is present.

The gate is intentionally strict to prevent synthetic or calculated data from being misrepresented as measured clinker quality.

## Status categories

### GO

The data package may proceed to formal analysis and scientific review.

### CONDITIONAL GO

The data package contains most required evidence, but one or more items require clarification, enrichment, or an explicit documented caveat before use.

### BLOCKED

The data package is not acceptable for clinker-target analysis or direct industrial process modeling.

## Acceptance criteria

A dataset may pass only if all of the following are true:

1. Target is measured.
   - The primary target must be obtained by measurement, not by calculation or inference.
   - Bogue values are not accepted as measured ground truth.

2. Measurement method is documented.
   - XRF, XRD, Rietveld, titration, or other methods must be explicitly described.

3. Sample ID exists.
   - Each clinker and material sample must have a unique identifier.

4. Units are known.
   - All values must carry unit information and basis information where relevant.

5. Provenance exists.
   - Material source, plant, kiln, and production line identity must be traceable.

6. Raw/process linkage exists where required.
   - Raw-mix and kiln process linkage must be available for the relevant analysis window.

7. Timestamp information exists.
   - Material sampling, raw mix, kiln run, and clinker sample timing must be captured.

8. Temporal alignment can be justified.
   - The researcher must be able to show that samples are aligned in time and operational context.

9. No target leakage exists.
   - Features used in analysis must not include future or post-measurement target values.

10. Data quantity is sufficient for the proposed experiment.
   - The sample count must be appropriate for the intended modeling or inference task.

## Hard blockers

The dataset is BLOCKED if any of the following applies:

- target values are generated from Bogue calculations or stoichiometric approximation
- the dataset includes only synthetic or simulated clinker records
- the records cannot be linked to a real raw mix or kiln run
- timestamps are missing or unusable
- measurements are unlabeled as measured/calculated/estimated
- there are no clear laboratory or field methods for the recorded clinker quality metrics
- the dataset lacks sample IDs or provenance information

## Example gate outcomes

### GO

A dataset with measured clinker chemistry, XRD phase analysis, timed raw-mix records, kiln telemetry, and clear provenance qualifies for further structured analysis.

### CONDITIONAL GO

A dataset has measured clinker chemistry but incomplete process linkage or incomplete raw-mix metadata. It may proceed only with specific caveats and a documented scope limitation.

### BLOCKED

A dataset with only calculated clinker phases, synthetic clinker targets, or unlabeled Bogue estimates is blocked.

## Reporting standard

Each candidate dataset should be labeled with:

- dataset status
- missing field list
- provenance gap list
- measurement method summary
- time alignment summary
- dataset sufficiency for the intended experiment

## Final decision rule

The project may proceed only after the data package satisfies the acceptance gate and retains a clean distinction between:

- MEASURED INPUT
- CALCULATED OUTPUT
- REFERENCE ESTIMATE
- SYNTHETIC OR DEMO DATA

No clinker-quality prediction work may begin without this gate being cleared.
