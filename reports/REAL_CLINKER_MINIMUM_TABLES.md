# MINIMUM REQUIRED CLINKER TABLES

## 1) clinker_samples.csv

The following schema is proposed as the minimum practical clinker sample table.

### REQUIRED
- Sample_ID
- Plant_ID
- Kiln_ID
- Production_DateTime
- Sampling_DateTime
- Raw_Mix_ID
- Kiln_Run_ID
- CaO_wt_pct
- SiO2_wt_pct
- Al2O3_wt_pct
- Fe2O3_wt_pct
- MgO_wt_pct
- SO3_wt_pct
- Na2O_wt_pct
- K2O_wt_pct
- Free_CaO_wt_pct
- C3S_wt_pct
- C2S_wt_pct
- C3A_wt_pct
- C4AF_wt_pct
- Phase_Measurement_Method
- Oxide_Measurement_Method
- Lab_ID
- Measurement_DateTime
- Quality_Flag
- Source

### HIGHLY DESIRABLE
- Material_Lot_ID
- Source_ID
- Feed_Rate
- Fuel_Rate
- Kiln_Feed_Composition_ID
- Residence_Time_Minutes
- Sampling_Delay_Minutes
- Production_Window_Start
- Production_Window_End
- Measurement_Uncertainty

### OPTIONAL
- Na2O_wt_pct
- K2O_wt_pct
- Cl_wt_pct
- LOI_wt_pct
- Notes
- Raw_Material_Recipe_Reference
- Data_Status
- License_Status

## 2) kiln_process.csv

The following process table should include only variables needed for valid process-state modeling.

### ONLINE PROCESS VARIABLES
- Timestamp
- Plant_ID
- Kiln_ID
- Kiln_Feed_Rate
- Kiln_Speed
- Burning_Zone_Temperature
- Calciner_Temperature
- Preheater_Temperatures
- O2
- CO
- CO2
- Fuel_Rate
- Fuel_Type
- Pressure
- Draft
- Relevant DCS / SCADA tags

### POST-PRODUCTION CLINKER VARIABLES
- Clinker chemistry values measured after production
- Phase percentages measured after production
- Free CaO measured after production
- Lab method metadata
- Sample IDs
- Quality flags

Important rule:
Post-production clinker chemistry must not be treated as an online-control feature.

## 3) Temporal alignment requirements

Future data must provide:
- process timestamp
- raw-mix timestamp
- clinker sample timestamp
- production window
- sampling delay
- residence time if available

Naive nearest-timestamp matching is not acceptable for production-to-target alignment.

## 4) Target priority

Priority order for future targets should be:
1. Free CaO
2. C3S / alite
3. C2S / belite
4. C3A
5. C4AF
6. Clinker oxide chemistry

However, target priority must ultimately depend on:
- measurement availability
- measurement quality
- sample count
- traceability
- variation
- research usefulness

A target that does not exist in a measured form must not be forced into the dataset.

## 5) Separate research tracks

### TRACK A: Industrial raw-material/process → clinker prediction
Status: BLOCKED

### TRACK B: Measured clinker / XRD laboratory analysis
Status: Potentially available for future independent experiments

These tracks must remain separate. Track B does not solve Track A.
