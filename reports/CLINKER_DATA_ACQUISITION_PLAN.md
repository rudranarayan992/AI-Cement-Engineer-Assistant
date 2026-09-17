# CLINKER DATA ACQUISITION PLAN

## 1) Minimum required dataset

A real clinker ML dataset must be a measured industrial or laboratory dataset, not a generated demo. It must contain a direct, time-traceable link between raw feed, process conditions, clinker formation, and clinker quality measurements.

Minimum chain:

Raw material lots
    ↓
Raw mix / kiln feed recipe
    ↓
Kiln process state and residence-time window
    ↓
Clinker sample ID
    ↓
Measured clinker target (free CaO, XRD phase fractions, or XRF oxide chemistry)

## 2) Required columns

### Core identifiers
- `sample_id`
- `batch_id`
- `plant_id`
- `line_id`
- `kiln_id`
- `lab_sample_id`
- `timestamp` or `production_datetime`
- `sample_datetime`
- `source_id`

### Raw material inputs
- `material_id`
- `material_type`
- `material_lot_id`
- `material_share_pct`
- `cao_pct`
- `sio2_pct`
- `al2o3_pct`
- `fe2o3_pct`
- `mgo_pct`
- `so3_pct`
- `loi_pct`
- `moisture_pct`

### Raw mix / kiln feed
- `raw_mix_id`
- `mix_recipe_id`
- `mix_timestamp`
- `lsf`
- `sm`
- `am`
- `raw_meal_cao_pct`
- `raw_meal_sio2_pct`
- `raw_meal_al2o3_pct`
- `raw_meal_fe2o3_pct`
- `raw_meal_loi_pct`

### Process variables
- `kiln_temp_c`
- `preheater_temp_c`
- `calciner_temp_c`
- `feed_rate_tph`
- `fuel_rate_tph`
- `oxygen_pct`
- `co_pct`
- `pressure_kpa`
- `draft_pa`
- `kiln_speed_rpm`
- `secondary_air_temp_c`
- `residence_time_minutes`
- `ramp_rate_c_per_min`
- `burning_zone_temp_c`

### Clinker measurements
- `clinker_oxide_cao_pct`
- `clinker_oxide_sio2_pct`
- `clinker_oxide_al2o3_pct`
- `clinker_oxide_fe2o3_pct`
- `free_cao_pct`
- `c3s_pct_measured`
- `c2s_pct_measured`
- `c3a_pct_measured`
- `c4af_pct_measured`
- `measurement_method`
- `laboratory_method`
- `quality_flag`

## 3) Required measurement methods

For each target, the measurement method must be explicitly documented.

- Free CaO: ASTM/ISO-equivalent lab method or equivalent measured clinker test
- Clinker oxides: XRF with documented calibration and reference standards
- Phase fractions: XRD / QXRD / Rietveld or equivalent documented mineralogical method
- Process variables: plant historian or validated instrument entries

Bogue values are not allowed as ground truth. They may be used only as benchmark or reference output, never as the training label.

## 4) Required identifiers

The real dataset must contain:

- sample IDs
- lab sample IDs
- plant ID
- kiln ID or line ID
- batch ID
- raw material lot IDs
- source or supplier IDs
- timestamp IDs for mix, process, and lab result

A valid dataset cannot rely on a single `Batch_ID` without a documented production and lab chain.

## 5) Required timestamps

At minimum:

- raw material receipt/usage time
- raw mix/blend time
- kiln feed / process time
- clinker sampling time
- lab result time

The target must be aligned to the process with an explicitly validated residence time and sampling delay. No naive nearest-time join should be used when residence time matters.

## 6) Required process variables

The minimum online feature pack should include variables that are available before or at the time the clinker outcome is observed:

- raw material feed chemistry
- raw mix recipe and LSF/SM/AM
- raw meal chemistry
- kiln feed rate
- kiln zone temperatures
- oxygen, CO, pressure, draft
- fuel rate
- feed rate
- kiln speed
- cooler and secondary air conditions

The dataset should explicitly separate:

- MODEL_SET_ONLINE
- MODEL_SET_POST_PRODUCTION_DIAGNOSTIC

Post-production clinker XRD or XRF values should never be treated as online features unless they are actually available before prediction time.

## 7) Required clinker measurements

At least one of the following must be measured and traceable:

1. `free_cao_pct`
2. `c3s_pct_measured`
3. `c2s_pct_measured`
4. `c3a_pct_measured`
5. `c4af_pct_measured`
6. `clinker_oxide_*` measured by XRF

Prefer one clearly measured target first, then expand to the next target only when the dataset quality supports it.

## 8) Data-quality requirements

A real dataset must meet all of the following:

- valid sample/batch IDs
- documented measurement methods
- known units
- timestamps and time zone information
- acceptable missingness per variable
- data-quality flags
- duplicate detection
- no synthetic generation
- no Bogue-generated target labels
- no formula-derived target substitutions
- no target leakage

## 9) Provenance requirements

For each record, the provenance should document:

- source of the data
- plant or production site
- measurement lab
- method reference
- sample handling notes
- date and time of measurement
- analyst or system
- data-status flag (measured / calculated / simulated / missing)

The dataset must be traceable to an actual operating environment and measurement process.

## 10) License / data-use requirements

The data must have an explicit or documented use permission status.

- internal plant data: company approval required
- public benchmark data: license and citation requirement
- lab-generated data: data ownership and purpose-of-use statement

The field may be recorded as `data_usage_status` or `license_status`.

## 11) Acceptance checklist

Future data must satisfy all of the following before Step 13 is allowed:

[ ] Measured clinker target
[ ] XRD/Rietveld documented for phase targets
[ ] XRF documented for oxide chemistry
[ ] Sample IDs
[ ] Plant/kiln IDs
[ ] Timestamps
[ ] Raw-material linkage
[ ] Process linkage
[ ] Residence-time information
[ ] Sufficient observations
[ ] Missingness acceptable
[ ] No Bogue-generated ground truth
[ ] No synthetic labels
[ ] Provenance documented
[ ] License/data-use permission documented
[ ] Leakage audit passed

## 12) Recommended ways to obtain legitimate data

1. Internal plant production archive with lab sample records
2. Clinker production dataset from a plant with XRD/XRF lab results
3. Third-party industrial quality dataset with measurement documentation
4. A controlled pilot study covering feed, process, and clinker measurements

Do not accept generated demo files or Bogue estimates as a substitute for real data.

5. Validation workflow before model training
   - confirm target measurement method
   - confirm timings and sample IDs
   - confirm raw-material and production linkage
   - confirm no leakage
   - validate target quality and missingness
   - run Step 12 gate again

## 13) Final recommendation

The project is not ready for Step 13 until a real measured clinker dataset is obtained or validated. The current repository is insufficient because the available targets are generated outputs and the process chain lacks reliable traceability and timestamps.
