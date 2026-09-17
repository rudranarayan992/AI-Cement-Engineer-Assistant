# Data Collection Template for Real Cement / Clinker ML

This template defines the minimum schema and metadata that a plant and laboratory should provide before any cement/clinker ML model is trained.

This template is for real industrial data collection only. It does not describe the current repository.

## 1. General conventions

- Every table must include a timestamp and a source system identifier.
- Every sample must have a unique sample_id.
- Every batch or production interval must have a unique batch_id or production_interval_id.
- Every value must carry units.
- Every measurement must carry a method, instrument, and source.
- Every calculated variable must be marked as derived, not measured.
- Every target must be labeled as measured or derived.

## 2. Plant and equipment metadata template

Table: `plant_metadata`

| Column | Required | Unit / Format | Notes |
|---|---:|---|---|
| plant_id | Yes | string | Unique plant ID |
| line_id | Yes | string | Production line ID |
| kiln_id | Yes | string | Kiln ID |
| kiln_type | Yes | string | Dry, wet, SP, preheater, etc. |
| preheater_config | Yes | string | Number of stages, cyclone arrangement |
| precalciner_config | Yes | string | Type and configuration |
| production_capacity | Yes | tpd or tph | Nominal capacity |
| burner_type | Yes | string | Burner arrangement |
| cooler_type | Yes | string | Grate, planetary, etc. |
| raw_mill_type | Yes | string | Mill configuration |
| fuel_system | Yes | string | Coal, gas, alternative fuel, etc. |
| maintenance_window | Yes | timestamp range | Down time if relevant |
| data_source | Yes | string | DCS/SCADA/PLC | 

## 3. Raw material sample template

Table: `raw_material_samples`

| Column | Required | Unit / Format | Notes |
|---|---:|---|---|
| material_id | Yes | string | Material ID |
| material_type | Yes | string | Limestone, clay, sand, iron ore, etc. |
| source_id | Yes | string | Quarry, mine, supplier |
| sample_id | Yes | string | Unique sample ID |
| timestamp | Yes | ISO 8601 | Time of sample collection |
| plant_id | Yes | string | Plant reference |
| lot_id | Yes | string | Lot or delivery ID |
| SiO2 | Yes | wt% | Oxide analysis |
| Al2O3 | Yes | wt% | Oxide analysis |
| Fe2O3 | Yes | wt% | Oxide analysis |
| CaO | Yes | wt% | Oxide analysis |
| MgO | Yes | wt% | Oxide analysis |
| SO3 | Yes | wt% | Oxide analysis |
| Na2O | Yes | wt% | Oxide analysis |
| K2O | Yes | wt% | Oxide analysis |
| Cl | Yes | wt% | Chloride |
| LOI | Yes | wt% | Loss on ignition |
| moisture | Yes | wt% | As-received moisture |
| fineness | Optional | µm or m2/kg | Particle size or surface area |
| mineralogy_summary | Optional | string | Qualitative mineralogy |
| basis | Yes | string | Dry / as-received / ignited |
| analysis_method | Yes | string | XRF, wet chemistry, etc. |
| instrument | Yes | string | Lab instrument name |
| lab_id | Yes | string | Laboratory identifier |
| remarks | Optional | string | Notes |

## 4. Raw mix / kiln feed template

Table: `raw_mix_batches`

| Column | Required | Unit / Format | Notes |
|---|---:|---|---|
| batch_id | Yes | string | Unique raw mix batch ID |
| kiln_feed_batch_id | Yes | string | Feed batch if different |
| timestamp | Yes | ISO 8601 | Feed or batch time |
| plant_id | Yes | string | Plant ID |
| line_id | Yes | string | Line ID |
| material_id_1 ... n | Yes | string | Material IDs in the mix |
| proportion_1 ... n | Yes | wt% or mass | Actual blend proportions |
| total_mass | Yes | kg or t | Batch total |
| raw_feed_rate | Yes | t/h | Feed rate |
| feed_moisture | Yes | wt% | Feed moisture |
| kiln_feed_CaO | Yes | wt% | Composition |
| kiln_feed_SiO2 | Yes | wt% | Composition |
| kiln_feed_Al2O3 | Yes | wt% | Composition |
| kiln_feed_Fe2O3 | Yes | wt% | Composition |
| kiln_feed_MgO | Yes | wt% | Composition |
| kiln_feed_SO3 | Yes | wt% | Composition |
| LSF | Yes | dimensionless | Calculated formula |
| SM | Yes | dimensionless | Calculated formula |
| AM | Yes | dimensionless | Calculated formula |
| basis | Yes | string | Dry or ignited basis |
| sample_id | Yes | string | Feed sample ID |
| lab_id | Yes | string | Lab or source |
| notes | Optional | string | Additional info |

## 5. Kiln / process telemetry template

Table: `kiln_process_telemetry`

| Column | Required | Unit / Format | Notes |
|---|---:|---|---|
| timestamp | Yes | ISO 8601 | Time stamp |
| plant_id | Yes | string | Plant ID |
| line_id | Yes | string | Line ID |
| kiln_id | Yes | string | Kiln ID |
| process_window_id | Yes | string | Production interval ID |
| kiln_temp | Optional | °C | Kiln temperature |
| preheater_temp | Optional | °C | Preheater stage temp |
| calciner_temp | Optional | °C | Calciner temp |
| kiln_pressure | Optional | kPa or mbar | Pressure variable |
| O2 | Optional | % | Excess oxygen |
| CO | Optional | ppm or % | Combustion gas |
| draft | Optional | Pa or mbar | Draft / pressure |
| fuel_flow | Optional | t/h, Nm3/h, etc. | Fuel flow |
| fuel_type | Optional | string | Coal, gas, solid waste, etc. |
| kiln_speed | Optional | rpm | Rotary kiln speed |
| feed_rate | Optional | t/h | Feed rate |
| fan_speed | Optional | rpm | ID fan or kiln fan |
| cooler_air_flow | Optional | Nm3/h or m3/h | Cooling air |
| cooler_temp | Optional | °C | Cooler discharge / air temp |
| sensor_id | Yes | string | Sensor or tag ID |
| measurement_method | Yes | string | DCS/SCADA tag type |
| sampling_frequency | Yes | string | e.g., 1-minute |
| expected_role | Yes | string | Modelling role |

## 6. Clinker analysis template

Table: `clinker_measurements`

| Column | Required | Unit / Format | Notes |
|---|---:|---|---|
| clinker_sample_id | Yes | string | Sample ID |
| batch_id | Yes | string | Production batch |
| timestamp | Yes | ISO 8601 | Sampling time |
| plant_id | Yes | string | Plant ID |
| line_id | Yes | string | Line ID |
| kiln_id | Yes | string | Kiln ID |
| sample_location | Yes | string | Kiln discharge / cooler / lab |
| target_name | Yes | string | e.g. Free_CaO |
| target_value | Yes | numeric | Measured value |
| unit | Yes | string | wt%, MPa, etc. |
| measurement_method | Yes | string | XRF, XRD, Rietveld, wet chemistry |
| instrument | Yes | string | Instrument name |
| laboratory | Yes | string | Lab or source |
| measurement_label | Yes | string | One of allowed labels |
| sample_frequency | Yes | string | Daily / hourly / batch-specific |
| notes | Optional | string | Additional metadata |

Required measurement_label categories:

- MEASURED_XRD
- MEASURED_RIETVELD
- MEASURED_XRF
- MEASURED_LAB
- BOGUE_CALCULATED
- CHEMISTRY_DERIVED
- SYNTHETIC

## 7. Cement quality template

Table: `cement_quality`

| Column | Required | Unit / Format | Notes |
|---|---:|---|---|
| cement_sample_id | Yes | string | Sample ID |
| clinker_sample_id | Optional | string | Link to clinker |
| batch_id | Yes | string | Cement production batch |
| timestamp | Yes | ISO 8601 | Sampling time |
| plant_id | Yes | string | Plant ID |
| line_id | Yes | string | Line ID |
| cement_oxide_CaO | Optional | wt% | XRF oxide |
| cement_oxide_SiO2 | Optional | wt% | XRF oxide |
| cement_oxide_Al2O3 | Optional | wt% | XRF oxide |
| cement_oxide_Fe2O3 | Optional | wt% | XRF oxide |
| Blaine | Optional | cm2/g | Fineness |
| setting_time_initial | Optional | min | Setting time |
| setting_time_final | Optional | min | Setting time |
| soundness | Optional | mm | Autoclave or equivalent |
| compressive_strength_1d | Optional | MPa | If tested |
| compressive_strength_3d | Optional | MPa | If tested |
| compressive_strength_7d | Optional | MPa | If tested |
| compressive_strength_28d | Optional | MPa | If tested |
| test_standard | Yes | string | ASTM, EN, ISO, etc. |
| curing_age_days | Optional | integer | For strength tests |
| lab_id | Yes | string | Lab identifier |

## 8. Traceability and linkage template

Table: `production_linkage`

| Column | Required | Unit / Format | Notes |
|---|---:|---|---|
| raw_material_sample_id | Yes | string | Material sample |
| raw_mix_batch_id | Yes | string | Feed batch |
| kiln_feed_batch_id | Yes | string | Feed batch if separate |
| production_interval_id | Yes | string | Process interval |
| clinker_sample_id | Yes | string | Clinker sample |
| cement_sample_id | Yes | string | Cement sample |
| start_time | Yes | ISO 8601 | Production start |
| end_time | Yes | ISO 8601 | Production end |
| residence_time_estimate | Yes | min or h | Estimated delay |
| notes | Optional | string | Linkage explanation |

## 9. Data export checklist

Before export, confirm:

- all rows have timestamps
- all IDs are unique
- all units are standardized
- all measurement methods are named
- all targets have label classifications
- no synthetic values are included in the measured-target tables
- no derived variables are mislabeled as measured results
- process telemetry is aligned to production intervals
- raw materials are traceable to feed batches and clinker samples
- all laboratory tests cite standards and instruments

## 10. Minimum data quality requirements

The export must include quality flags for:

- duplicate sample IDs
- missing values
- impossible values
- sensor outage windows
- lab errors or outliers
- incomplete batch linkage
- mismatch between feed batch and clinker sample interval
- delayed or missing laboratory results

The exported dataset is not ready for modeling until these checks are complete.
