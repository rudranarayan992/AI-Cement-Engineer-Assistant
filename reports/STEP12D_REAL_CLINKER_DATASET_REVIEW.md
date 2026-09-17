# STEP 12D REAL CLINKER DATASET REVIEW

## 1) Executive summary

This review was limited to publicly identifiable scientific repositories and reference sources without downloading or modifying any dataset. The objective was to find a real clinker dataset that could satisfy the Step 12 gate for a true raw-material → kiln → clinker modeling task.

The clear conclusion is:

- Some public datasets contain measured clinker chemistry or XRD phase data, but they are laboratory or reference datasets, not full industrial training data.
- None of the reviewed public candidates was shown to contain a validated raw-material → process → clinker traceability chain with timestamps and plant/kiln identifiers.
- No public candidate was identified that genuinely satisfies the project’s Step 12 requirements for a real clinker ML training set.
- Bogue-derived phase values remain unacceptable as measured ground truth. Any dataset with `C3S`, `C2S`, `C3A`, `C4AF`, or `Free_CaO` must be checked carefully to confirm whether those values are measured by XRD/XRF/lab methods or calculated from chemistry.

The best public candidates are reference and laboratory datasets that can support validation, phase-analysis methods, and scientific benchmarking, but they do not qualify as full industrial training data for the original AI Cement Engineer objective.

## 2) Dataset candidates

### A. FULL INDUSTRIAL TRAINING DATA

This category requires a real industrial chain: raw materials → kiln process → clinker sample → measured clinker target with sample IDs, timestamps, and traceability. No public candidate identified in this review meets this standard.

#### Candidate A1: No verified public full industrial clinker training dataset found
- Dataset name: none verified
- URL: none verified
- Repository: none verified in this review
- Number of samples: not verified
- Classification: full industrial training data
- Measured or derived targets: not verified
- XRD available?: not verified
- Rietveld/QXRD available?: not verified
- XRF available?: not verified
- Free CaO available?: not verified
- C3S available?: not verified
- C2S available?: not verified
- C3A available?: not verified
- C4AF available?: not verified
- Raw-material chemistry available?: not verified
- Kiln/process data available?: not verified
- Timestamps available?: not verified
- Sample IDs available?: not verified
- Plant/kiln IDs available?: not verified
- Traceability available?: none verified
- Measurement method: not verified
- Provenance: not verified
- License: not verified
- Download availability: not verified
- Suitability for ML: no verified match found
- Limitations: no public dataset in this review shows full industrial traceability

### B. CLINKER LABORATORY DATA

These are real measured laboratory datasets, but they generally lack the plant process history needed for the project’s Step 12 goal.

#### Candidate B1: Rietveld quantitative phase analyses of SRM 2686a: a standard Portland clinker
- Dataset name: Rietveld Quantitative Phase Analyses of SRM 2686a: a Standard Portland Clinker
- URL: https://zenodo.org/records/1318501
- Repository: Zenodo
- Number of samples: one certified reference clinker sample with multiple diffraction configurations / patterns; not an industrial batch dataset
- Classification: clinker laboratory / reference measurement data
- Measured or derived targets: measured XRD-based phase data; not process-derived
- XRD available?: yes
- Rietveld/QXRD available?: yes
- XRF available?: possibly as part of the associated reference report, but not the main dataset focus
- Free CaO available?: not confirmed in this summary; likely not the key target of the record
- C3S available?: yes, as phase quantification from XRD/Rietveld analysis
- C2S available?: yes
- C3A available?: yes
- C4AF available?: yes, depending on analysis set
- Raw-material chemistry available?: no
- Kiln/process data available?: no
- Timestamps available?: not in a production sense; only lab/analysis timestamps not a plant process trace
- Sample IDs available?: likely sample ID / reference material ID, but not process traceability
- Plant/kiln IDs available?: no
- Traceability available?: limited to reference material provenance, not plant feed-to-product traceability
- Measurement method: XRD, Rietveld quantitative phase analysis; multiple powder diffraction configurations
- Provenance: NIST SRM 2686a reference clinker; cited in ASTM C1365 context
- License: Zenodo open access; check DOI metadata for exact license
- Download availability: yes, open download from Zenodo
- Suitability for ML: limited; useful for method validation and reference benchmarking, not for raw-material-to-kiln prediction
- Limitations: reference material only; no plant history; no industrial batch traceability; no throughput/time series

#### Candidate B2: Engineering Performance and Hydration Behavior of Low-Clinker Ternary Cementitious Systems Incorporating Fly Ash and Blast Furnace Slag
- Dataset name: Engineering Performance and Hydration Behavior of Low-Clinker Ternary Cementitious Systems Incorporating Fly Ash and Blast Furnace Slag
- URL: https://zenodo.org/records/18758773
- Repository: Zenodo
- Number of samples: not disclosed in the search summary; experimental lab set with multiple formulations
- Classification: clinker laboratory / cementitious-materials experiment
- Measured or derived targets: measured formulation and quantitative XRD results, plus strength results
- XRD available?: yes
- Rietveld/QXRD available?: yes, the summary explicitly states quantitative XRD results (Rietveld method)
- XRF available?: not stated in the summary
- Free CaO available?: not stated
- C3S available?: likely as phase quantification from XRD analysis of cementitious systems
- C2S available?: likely
- C3A available?: likely
- C4AF available?: likely in clinker-derived phases
- Raw-material chemistry available?: possibly as formulation data
- Kiln/process data available?: no
- Timestamps available?: likely test-age timestamps, but not plant production timestamps
- Sample IDs available?: likely yes, sample or mix identifiers, but not production process lineage
- Plant/kiln IDs available?: no
- Traceability available?: no full plant traceability
- Measurement method: XRD/Rietveld, strength testing, calorimetry, thermogravimetric analysis
- Provenance: published experimental dataset tied to a manuscript
- License: Zenodo open access; check exact license field on record
- Download availability: yes
- Suitability for ML: moderate for formulation and hydration modeling, but not valid as an industrial clinker process dataset
- Limitations: not a kiln production dataset; no process metrics; no timestamped plant chain

#### Candidate B3: Synthesis of Sulfate-Resistant Cement Through “Green” Technology Using Karakalpakstan Raw Materials
- Dataset name: Synthesis of Sulfate-Resistant Cement Through “Green” Technology Using Karakalpakstan Raw Materials
- URL: https://zenodo.org/records/17607432
- Repository: Zenodo
- Number of samples: small experimental set; not clearly a large industrial dataset
- Classification: clinker laboratory / material synthesis study
- Measured or derived targets: phase fractions reported from XRD; formulation-based synthesis
- XRD available?: yes
- Rietveld/QXRD available?: the abstract states XRD analysis identified alite/belite etc.; likely phase quantification but not necessarily full Rietveld metadata
- XRF available?: possible as oxide composition analysis, not clear from the summary
- Free CaO available?: not clearly stated
- C3S available?: yes, approx. 38.6% reported
- C2S available?: yes, approx. 41.0%
- C3A available?: yes, low percentage
- C4AF available?: yes, approx. 16.2%
- Raw-material chemistry available?: likely yes, because local raw materials are described
- Kiln/process data available?: no
- Timestamps available?: not a plant process time series
- Sample IDs available?: likely sample IDs or mix labels, but not production traceability
- Plant/kiln IDs available?: no
- Traceability available?: not industrial traceability
- Measurement method: XRD and sulfur-resistant cement tests (ASTM C1012/C1012M style durability tests)
- Provenance: lab synthesis experiment published as an article/dataset
- License: Zenodo open access; exact license depends on record metadata
- Download availability: yes
- Suitability for ML: low for industrial clinker prediction; potentially useful for experimental phase-analysis benchmarking
- Limitations: small, synthetic or lab-synthesis dataset; no plant or kiln operating history

#### Candidate B4: Oxyfuel clinker cooler operational performance dataset
- Dataset name: D9.2 – Analysis of oxyfuel clinker cooler operational performance
- URL: https://zenodo.org/records/2605063
- Repository: Zenodo
- Number of samples: industrial test set; likely small operational campaign, not a continuous production dataset
- Classification: industrial pilot / clinker process trial
- Measured or derived targets: clinker quality and cooler performance observations; not a general full-scale production dataset
- XRD available?: possibly in the study discussion; not clearly a complete phase table
- Rietveld/QXRD available?: not clearly stated
- XRF available?: possible, but not confirmed from the summary
- Free CaO available?: not clearly confirmed
- C3S available?: maybe as part of clinker quality results, but not guaranteed
- C2S available?: maybe
- C3A available?: maybe
- C4AF available?: maybe
- Raw-material chemistry available?: likely not at full industrial chain resolution
- Kiln/process data available?: yes for an oxyfuel cooler test campaign; process/operation metrics are present
- Timestamps available?: likely yes for trial data, but not a production feed-to-product time series
- Sample IDs available?: likely yes for process samples, but not guaranteed from summary
- Plant/kiln IDs available?: likely a specific plant ID or process test context, but not sufficient for general ML
- Traceability available?: partial only; pilot plant not general industrial chain
- Measurement method: clinker tests and process observation during a plant trial
- Provenance: industrial pilot project data from an EU research program
- License: Zenodo open access; check license metadata on the record
- Download availability: yes
- Suitability for ML: low-to-moderate for an industrial trial model, but still not a full raw-material-to-kiln trading dataset; insufficient for the Step 12 gate
- Limitations: pilot-scale, small operating window, no full training dataset required by Step 12

### C. XRD DATA

These are X-ray diffraction datasets or pattern files. They may be useful to check phase-analysis methods, but they do not satisfy the project’s requirement for plant-linked measured clinker targets.

#### Candidate C1: SRM 2686a Rietveld analysis pattern set
- Dataset name: Rietveld Quantitative Phase Analyses of SRM 2686a: Standard Portland Clinker (pattern files)
- URL: https://zenodo.org/records/1318501
- Repository: Zenodo
- Number of samples: multiple diffraction patterns; not a production dataset
- Classification: XRD data / reference patterns
- Measured or derived targets: measured XRD patterns and quantitative phase values; not a full industrial target dataset
- XRD available?: yes
- Rietveld/QXRD available?: yes
- XRF available?: no, not the main content
- Free CaO available?: not the principal target in the pattern dataset
- C3S available?: yes, as phase analysis results
- C2S available?: yes
- C3A available?: yes
- C4AF available?: yes
- Raw-material chemistry available?: no
- Kiln/process data available?: no
- Timestamps available?: no production timestamps
- Sample IDs available?: likely only reference material ID, not process-chain sample IDs
- Plant/kiln IDs available?: no
- Traceability available?: none beyond reference material identity
- Measurement method: powder diffraction, Rietveld analysis, multiple geometries
- Provenance: NIST reference clinker and research analysis protocol
- License: Zenodo open access; confirm exact record license
- Download availability: yes
- Suitability for ML: useful for phase-analysis validation only; not suitable for an industrial clinker process model
- Limitations: not a full dataset; no raw material or kiln history; single reference material context

#### Candidate C2: Nano-crystalline C-S-H XRD profile data
- Dataset name: Data for “Quantification of nano-crystalline C-S-H in hydrated C3S, Portland cement and fly ash c…”
- URL: https://zenodo.org/records/13979407
- Repository: Zenodo
- Number of samples: experimental hydration samples, not clinker production records
- Classification: XRD / hydration analysis data
- Measured or derived targets: measured diffraction and extracted profile data, not a clinker process dataset
- XRD available?: yes
- Rietveld/QXRD available?: yes, profile extraction and Rietveld analysis are described
- XRF available?: not central to the record
- Free CaO available?: not relevant here
- C3S available?: yes as hydrated C3S sample content; but not as a plant-production target
- C2S available?: not the main target
- C3A available?: not the main target
- C4AF available?: not the main target
- Raw-material chemistry available?: not as a plant-level chain
- Kiln/process data available?: no
- Timestamps available?: mostly hydration-age data, not production timestamps
- Sample IDs available?: likely experimental sample IDs
- Plant/kiln IDs available?: no
- Traceability available?: no industrial traceability
- Measurement method: XRD and Rietveld/PONKCS analysis
- Provenance: published research dataset
- License: Zenodo open access; exact record license to verify
- Download availability: yes
- Suitability for ML: not for clinker-process prediction; good for XRD analytical method work only
- Limitations: cement hydration dataset, not kiln-linked clinker dataset

### D. REFERENCE MATERIALS

These are small, certified reference sets or lab reference samples. They are scientifically valuable but not equivalent to full production training data.

#### Candidate D1: NIST SRM 2686a Portland clinker reference material
- Dataset name: SRM 2686a (standard Portland clinker reference material)
- URL: https://shop.nist.gov/ (product search / NIST SRM catalog)
- Repository: NIST
- Number of samples: one certified reference material; not a large industrial dataset
- Classification: reference material
- Measured or derived targets: certified reference clinker material; phase values are measured and reference-certified, but not a production process dataset
- XRD available?: yes, as reference material used for method validation and phase analysis
- Rietveld/QXRD available?: yes, this material is used in ASTM C1365 validation
- XRF available?: sometimes part of method validation but not the main metrological content
- Free CaO available?: not generally the central item in the reference material description
- C3S available?: yes, reference phase values may be reported by a qualified analysis method
- C2S available?: yes
- C3A available?: yes
- C4AF available?: yes
- Raw-material chemistry available?: no
- Kiln/process data available?: no
- Timestamps available?: no
- Sample IDs available?: yes, reference material ID
- Plant/kiln IDs available?: no
- Traceability available?: limited to reference material traceability, not process-line traceability
- Measurement method: certified reference material and XRD/Rietveld as a validation standard
- Provenance: NIST reference material and ASTM validation context
- License: NIST standard reference material; use and citation policy applies
- Download availability: available by order through NIST store / certification docs
- Suitability for ML: not suitable for industrial process prediction because it is a reference sample, not a production dataset
- Limitations: small number of samples; no plant, no time series, no raw-material traceability

### E. UNSUITABLE DATA

These repositories or records were identified as part of the public search but did not contain any verified full industrial clinker data for the Step 12 goal.

#### Candidate E1: Zenodo general clinker/cement XRD and materials results
- Dataset name: several articles and datasets such as the Karakalpakstan synthesis study, hydration studies, and low-clinker formulations
- URL: Zenodo search results pages (for example: https://zenodo.org/search?q=clinker%20xrd and https://zenodo.org/search?q=cement%20clinker%20xrd%20rietveld)
- Repository: Zenodo
- Number of samples: low-to-moderate experimental set; not a full process dataset
- Classification: laboratory / experimental / not industrial production
- Measured or derived targets: often measured XRD or material testing, but not a plant-linked dataset
- XRD available?: often yes
- Rietveld/QXRD available?: often yes
- XRF available?: not always
- Free CaO available?: not consistently
- C3S/C2S/C3A/C4AF available?: sometimes yes, but often as phase estimates or phase-quantified lab outputs
- Raw-material chemistry available?: sometimes, but not in a production-chain sense
- Kiln/process data available?: no
- Timestamps available?: not process timestamps
- Sample IDs available?: usually limited or not directly tied to operation history
- Plant/kiln IDs available?: no
- Traceability available?: no
- Measurement method: lab methods only
- Provenance: publication- or lab-derived, but not an industrial production archive
- License: open on Zenodo, but per-record metadata must be checked
- Download availability: yes
- Suitability for ML: unsuitable for Step 12 plant prediction; only useful for method benchmarking and experimental analysis
- Limitations: not a plant dataset; not raw-material-to-clinker traceable; often small-n and study-specific

#### Candidate E2: Dryad search results
- Dataset name: no verified clinker/production dataset found in the targeted Dryad pass
- URL: https://datadryad.org/
- Repository: Dryad
- Number of samples: not applicable in this pass
- Classification: not verified as clinker-related in this review
- Measured or derived targets: not verified
- XRD available?: not verified
- Rietveld/QXRD available?: not verified
- XRF available?: not verified
- Free CaO available?: not verified
- C3S/C2S/C3A/C4AF available?: not verified
- Raw-material chemistry available?: not verified
- Kiln/process data available?: not verified
- Timestamps available?: not verified
- Sample IDs available?: not verified
- Plant/kiln IDs available?: not verified
- Traceability available?: not verified
- Measurement method: not verified
- Provenance: repository is valid but the specific clinker dataset was not identified in this review
- License: Dryad metadata typically includes a DOI and data publication license, but no clinker dataset was confirmed here
- Download availability: repository is open but this review found no verified clinker candidate in the targeted search
- Suitability for ML: no verified candidate identified
- Limitations: no direct clinker dataset proved in this review

#### Candidate E3: Figshare search results
- Dataset name: no verified clinker dataset found in the targeted Figshare pass; the site blocks automated browser checks and requires JS-enabled browsing
- URL: https://figshare.com/
- Repository: Figshare
- Number of samples: not applicable in this pass
- Classification: not verified as clinker-related
- Measured or derived targets: not verified
- XRD available?: not verified
- Rietveld/QXRD available?: not verified
- XRF available?: not verified
- Free CaO available?: not verified
- C3S/C2S/C3A/C4AF available?: not verified
- Raw-material chemistry available?: not verified
- Kiln/process data available?: not verified
- Timestamps available?: not verified
- Sample IDs available?: not verified
- Plant/kiln IDs available?: not verified
- Traceability available?: not verified
- Measurement method: not verified
- Provenance: not verified in this targeted pass
- License: not verified in this targeted pass
- Download availability: repository is open, but no verified clinker candidate emerged in this review
- Suitability for ML: none identified
- Limitations: no verified clinker match in this review

#### Candidate E4: Mendeley Data / Kaggle
- Dataset name: no verified clinker dataset found in the targeted review pass
- URL: https://data.mendeley.com/ and Kaggle search results (not recommended unless license and provenance are confirmed)
- Repository: Mendeley Data / Kaggle
- Number of samples: not applicable in this pass
- Classification: not verified
- Measured or derived targets: not verified
- XRD available?: not verified
- Rietveld/QXRD available?: not verified
- XRF available?: not verified
- Free CaO available?: not verified
- C3S/C2S/C3A/C4AF available?: not verified
- Raw-material chemistry available?: not verified
- Kiln/process data available?: not verified
- Timestamps available?: not verified
- Sample IDs available?: not verified
- Plant/kiln IDs available?: not verified
- Traceability available?: not verified
- Measurement method: not verified
- Provenance: not verified; Kaggle only accepted with clear provenance and license audit
- License: not verified in this pass
- Download availability: yes in principle, but not a validated Step 12 candidate here
- Suitability for ML: not confirmed
- Limitations: high risk of weak provenance or license ambiguity; requires manual source review

## 3) Measurement methods

The key rule is that a dataset must not be accepted merely because it contains columns such as `C3S`, `C2S`, `C3A`, `C4AF`, or `Free_CaO`. Those values must be checked for method provenance.

The acceptable measurement classes are:

- XRF for clinker and cement oxide chemistry
- XRD or QXRD for phase identification and quantitative phase analysis
- Rietveld quantitative analysis for clinker phase fractions
- ASTM / ISO equivalent free-CaO testing methods
- Lab-certified reference materials, e.g., NIST SRM

The unacceptable classes are:

- Bogue-derived phase calculations
- chemistry-derived substitutes for measured phase values
- synthetic or formula-generated targets
- inferred phase values without documented lab method

Bogue-derived phases are not accepted as measured ground truth. They are engineering estimates and cannot satisfy the Step 12 data qualification gate.

## 4) Target qualification

For all candidates reviewed, qualification depends on whether each target was measured directly or computed.

- NIST SRM 2686a / Rietveld pattern set: target values are measured and reference-validated, but only as a reference material, not a plant production dataset.
- Experimental XRD datasets: often measured, but not linked to industrial process history.
- Industrial pilot datasets: may contain measured clinker samples or process data, but typically not the full raw-material → kiln → clinker traceability required by Step 12.
- Generated or formula-derived values in the project: unacceptable and explicitly excluded.

## 5) Traceability

The Step 12 requirement is not just “has measured clinker chemistry,” but “has measured clinker chemistry with traceability.”

This means the dataset must show a defensible path from:

- raw material lot / source / chemistry
- raw mix / kiln feed recipe
- kiln process state / operating window
- clinker sample / lab sample ID
- measured clinker target by method

The public candidates reviewed here generally fail the traceability requirement because they are either:

- reference materials,
- lab experimental papers,
- XRD pattern archives,
- or small pilot studies without a full process chain.

## 6) Temporal information

No public candidate identified in this review provides both:

- a valid time-stamped production history, and
- a direct sample-to-target linkage from raw feed to clinker product.

This is the central blocker. Without timestamps and residence-time logic, even a measured clinker target does not qualify for the project’s original Step 12 requirement.

## 7) Provenance

Public datasets from Zenodo and NIST are generally better than random internet data because they usually include:

- DOI or metadata
- author or institution information
- publication context
- sample provenance and method description

However, provenance alone does not satisfy the project requirement. A dataset still must be a valid industrial process dataset with a production chain and a target measured by an accepted method.

## 8) License

Public repositories like Zenodo and NIST generally provide open access or standard repository licenses; however, the exact terms still need to be checked at the record level. This is especially important for any dataset that will be reused in ML development.

For the project’s current scientific gate, however, license is secondary to data validity. The first question is whether the data are real, measured, traceable, and usable. Current public candidates fail that broader validity question.

## 9) Suitability classification

### A. Full industrial training data
- Status: no verified public candidate found

### B. Clinker laboratory data
- Status: real measured clinker or we-verified XRD/phase datasets exist, but they are not full process-linked industrial datasets
- Examples: SRM 2686a reference analysis, experimental XRD datasets, low-clinker lab studies, etc.

### C. XRD data
- Status: available in several pattern-based and Rietveld datasets
- Examples: SRM 2686a XRD patterns, C-S-H XRD profile datasets

### D. Reference materials
- Status: NIST SRM 2686a is the strongest public reference candidate

### E. Unsuitable data
- Status: general Zenodo / Dryad / Figshare / Mendeley / Kaggle searches did not produce a verified Step 12-compliant industrial clinker dataset in this review

## 10) Research strategy comparison

### Strategy A: Find full plant-linked industrial clinker dataset
Advantages:
- would satisfy the original AI Cement Engineer objective directly
- supports prediction from raw-material and process variables to clinker quality
- best scientifically and operationally

Limitations:
- rare in public repositories
- requires plant/lab cooperation or a carefully curated industrial archive
- may require legal and IP review

Research value:
- highest

Data requirements:
- process time series
- raw material lots and chemistry
- feed composition and kiln conditions
- measured clinker targets with lab methods
- timestamps and sample IDs

Supports the original goal?
- yes, directly

### Strategy B: Use measured clinker laboratory/XRD data for a clinker-quality model while excluding plant-process prediction
Advantages:
- uses real measured targets
- scientifically defensible if the task is formulation or phase-analysis modeling
- easier to obtain than plant-linked industrial data

Limitations:
- does not satisfy the original raw-material/process-to-clinker goal
- may still lack large-n sampling and full traceability
- not equivalent to industrial prediction

Research value:
- moderate

Data requirements:
- measured phase fractions or oxide chemistry by XRF/XRD
- laboratory metadata
- sample IDs and method labels
- no plant history required

Supports the original goal?
- not fully; only partially supports a separate scientific task

### Strategy C: Use a reference/XRD dataset only for a separate XRD/phase-analysis module
Advantages:
- realistic and scientifically valid
- supports validation of phase quantification methods
- useful for XRD interpretation and reference benchmarking

Limitations:
- not a production-predictive dataset
- not suitable for clinker process prediction or AI Cement Engineer pipeline

Research value:
- moderate for analytical work, low for full process ML

Data requirements:
- XRD patterns and phase-analysis results
- reference material IDs and calibration metadata

Supports the original goal?
- only as a secondary module, not as the primary dataset

### Strategy D: Acquire original plant/laboratory data through collaboration
Advantages:
- best route to a valid Step 12 dataset
- can capture true industrial traceability and process behavior
- align with the required scientific standard

Limitations:
- time-consuming
- requires operator or university collaboration
- may require non-disclosure and legal approvals

Research value:
- highest

Data requirements:
- plant/lab partnership
- raw material and production records
- measured clinker targets and lab methods
- timestamps, sample IDs, plant IDs, kiln IDs

Supports the original goal?
- yes, if the data truly satisfy the gate

## 11) Recommended dataset

The strongest public candidate is:

- NIST SRM 2686a reference clinker with associated Rietveld/XRD analyses (Zenodo + NIST reference material context)

Why this is the best candidate:
- real measured clinker reference material
- XRD/Rietveld methodology is clearly documented
- suitable for method validation and benchmarking
- available as open scientific reference material

Why it is not enough for Step 12:
- it is a reference material, not a full industrial production dataset
- no raw-material feed chain or kiln process history
- no production timestamps and no plant traceability
- no valid industrial ML training sample set

## 12) Remaining gaps

The public domain still lacks, in one place, a dataset with all of the following:

- raw-material lots and chemistry
- raw-mix composition and recipe history
- kiln process variables and operating window
- residence time / lag information
- real kiln or plant IDs
- clinker sample IDs and lab IDs
- measured target values from XRF/XRD/free-CaO tests
- sample timestamps and production alignment
- cross-table traceability from feed to clinker
- documented provenance and licensing

Without these, Step 12 still fails.

## 13) Exact next action

The next action is not model training and not Step 13. The required action is external acquisition of a real industrial or university-lab clinker dataset that satisfies the raw-material → kiln → clinker measurement chain and passes the Step 12 gate.

The project should target:

- a plant or lab partner with measured clinker XRD/XRF data,
- raw-material chemistry and blend records,
- kiln process log data,
- timestamps and sample IDs,
- and explicit method documentation

Only after such a dataset is acquired and qualified can Step 12 be re-evaluated.

## Acceptance table

| Candidate | Real measured? | XRD | XRF | Free CaO | C3S/C2S/C3A/C4AF | Process data | Timestamps | Traceability | License | ML suitability |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| NIST SRM 2686a reference clinker | Yes, reference-measured | Yes | Possibly in method validation context | Not clearly central | Yes, phase quantification available | No | No production timestamps | Limited to reference material only | NIST policy / record metadata | Not suitable for industrial training |
| SRM 2686a Zenodo pattern set | Yes, measured diffraction data | Yes | No | Not central | Yes, from phase analysis | No | No | Reference material only | Open Zenodo record | Not suitable for industrial training |
| Zenodo low-clinker lab dataset | Yes, measured lab study | Yes | Not clearly stated | Not stated | Likely yes, as phase fractions | No | Not production time series | No | Open Zenodo record | Low |
| Zenodo sulfate-resistant clinker synthesis study | Yes, measured lab study | Yes | Possibly | Not clearly stated | Yes | No | No | No | Open Zenodo record | Low |
| Zenodo oxyfuel clinker cooler trial | Partial / industrial pilot | Possibly | Possible | Not confirmed | Possibly | Yes, pilot process data | Likely yes for trial window | Partial, pilot only | Open Zenodo record | Low-to-moderate, but still not Step 12 compliant |
| Zenodo general XRD / hydration datasets | Yes, measured lab data | Yes | Sometimes | Sometimes | Sometimes | No | Not plant process time series | No | Open Zenodo record | Very low |
| Dryad search / no verified candidate | Not verified | Not verified | Not verified | Not verified | Not verified | Not verified | Not verified | Not verified | Repository license varies | No verified candidate |
| Figshare search / no verified candidate | Not verified | Not verified | Not verified | Not verified | Not verified | Not verified | Not verified | Not verified | Repository license varies | No verified candidate |
| Mendeley/Kaggle / no verified candidate | Not verified | Not verified | Not verified | Not verified | Not verified | Not verified | Not verified | Not verified | Must be confirmed | Not recommended without provenance audit |

## Final decision

B. DATA IS USEFUL BUT STEP 12 STILL FAILS

This is the correct decision because public measured clinker/XRD data exist and are scientifically valuable, but none of the reviewed candidates satisfies the full Step 12 requirement for industrial raw-material → kiln → clinker traceability with measured targets and timestamps.
