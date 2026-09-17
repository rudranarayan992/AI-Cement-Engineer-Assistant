# NEXT DATA ACTION

## Classification

C. NEEDS EXTERNAL REAL CLINKER DATA

## 1) Exact dataset we need

A measured clinker production dataset from a real kiln or lab program, containing raw-material lots, raw-mix composition, kiln process operating conditions, clinker sampling, and measured clinker targets. The dataset must be traceable to an actual plant or laboratory process and must not be generated from formulas or Bogue equations.

## 2) Minimum required columns

Required identifiers:
- `sample_id`
- `lab_sample_id`
- `batch_id`
- `plant_id`
- `line_id`
- `kiln_id`
- `material_id`
- `material_lot_id`
- `source_id`
- `timestamp`
- `sample_datetime`

Required raw-material features:
- `material_type`
- `material_share_pct`
- `cao_pct`
- `sio2_pct`
- `al2o3_pct`
- `fe2o3_pct`
- `mgo_pct`
- `so3_pct`
- `loi_pct`
- `moisture_pct`

Required raw-mix / kiln-feed features:
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

Required kiln / process features:
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
- `burning_zone_temp_c`

Required target columns:
- `free_cao_pct`
- `c3s_pct_measured`
- `c2s_pct_measured`
- `c3a_pct_measured`
- `c4af_pct_measured`
- `clinker_oxide_cao_pct`
- `clinker_oxide_sio2_pct`
- `clinker_oxide_al2o3_pct`
- `clinker_oxide_fe2o3_pct`
- `measurement_method`
- `lab_id`
- `quality_flag`

## 3) Minimum measurement requirements

At least one target must be measured by a documented laboratory method and traceable to a sample.

Required measurement methods:
- Free CaO: ASTM or equivalent measured clinker lab method
- Oxide chemistry: XRF with calibration and reference standards
- Phase fractions: XRD / QXRD / Rietveld or equivalent
- Process variables: plant historian / DCS / validated instrumentation

Bogue-derived values are not acceptable as ground truth.

## 4) Required sample IDs

The dataset must include:
- unique `sample_id`
- unique `lab_sample_id`
- unique `batch_id`
- plant ID
- kiln ID or line ID
- raw material lot ID
- source ID
- production interval ID
- chain link from raw material to clinker sample

A single `Batch_ID` without sample and lab provenance is not enough.

## 5) Required timestamps

Required timestamps:
- raw material receipt / use time
- raw mix recipe time
- kiln feed time
- production interval start and end
- clinker sampling time
- lab measurement time
- analysis result time

The target must be aligned with the process using explicit residence-time and sample-delay logic.

## 6) Required process/raw-material linkage

The dataset must explicitly link:
- raw material lots to blend recipe
- raw mix to kiln feed composition
- kiln process window to clinker sample
- clinker sample to lab measurement
- lab measurement to sample ID and batch ID

No synthetic row-level join with a single `Batch_ID` is acceptable without real production traceability.

## 7) Required target measurement method

A valid target requires an explicit method tag such as:
- `MEASURED_XRF`
- `MEASURED_XRD`
- `MEASURED_RIETVELD`
- `MEASURED_LAB`

Not acceptable:
- `BOGUE_CALCULATED`
- `CHEMISTRY_DERIVED`
- `SYNTHETIC`

## 8) Minimum acceptable sample count

Minimum acceptable initial sample count: 300 valid measured clinker observations.

Preferred: 500+ measured samples with a clear train/validation/test split and documented temporal holdout.

## 9) Provenance requirements

Each record must document:
- plant / site
- line / kiln
- raw material source
- lot / delivery details
- sampling location
- analyst / lab
- instrument model
- method reference
- measurement date and time
- data status (`measured`, `calculated`, `simulated`, `missing`)
- data use permissions or license

## 10) License/data-use requirements

The dataset must have explicit data-use status:
- internal plant data: company approval required
- public benchmark data: citation or license requirement
- lab-generated data: ownership and purpose-of-use statement

The table should include `data_usage_status` or `license_status`.

## 11) Acceptance checklist

[ ] Measured clinker target exists
[ ] XRD / Rietveld / XRF method documented
[ ] Sample IDs exist
[ ] Plant and kiln IDs exist
[ ] Timestamps exist
[ ] Raw-material linkage exists
[ ] Process linkage exists
[ ] Residence-time metadata exists
[ ] Minimum sample count met
[ ] Missingness acceptable
[ ] No Bogue-derived labels used as ground truth
[ ] No synthetic labels or formula-generated targets
[ ] Provenance documented
[ ] License / data-use status documented
[ ] Leakage audit passed
[ ] Step 12 gate re-run successfully

## Final action

Acquire a real clinker dataset from a plant or lab archive, verify measurement method and traceability, then re-run the Step 12 gate before any Step 13 work.
