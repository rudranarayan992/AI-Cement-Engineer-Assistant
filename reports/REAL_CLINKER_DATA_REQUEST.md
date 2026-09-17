# REAL CLINKER DATA REQUEST

This package is intended for a cement plant, cement R&D laboratory, university cement laboratory, or industrial research partner.

The objective is to obtain the minimum practical dataset needed to qualify a real clinker ML dataset under the project’s Step 12 gate.

## Requested data categories

### A. Plant / kiln metadata
- Plant ID
- Line ID
- Kiln ID
- Kiln type
- Preheater configuration
- Calciner configuration
- Production capacity
- Burner type
- Cooler type
- Raw mill configuration
- Fuel system
- Maintenance / downtime windows
- Control system source
- Production schedule details

### B. Raw-material chemistry
- Material ID
- Material type
- Source / quarry / mine / supplier
- Material lot ID
- Analysis timestamp
- CaO, SiO2, Al2O3, Fe2O3, MgO, SO3, Na2O, K2O, Cl, LOI
- Moisture
- Basis (as received / dry / ignited)
- Measurement method
- Lab ID
- Analyst / instrument
- Data status

### C. Raw-mix / raw-meal data
- Raw mix ID
- Batch ID
- Production interval ID
- Recipe proportions by material
- Blend weights or mass fractions
- Raw meal chemistry
- LSF, SM, AM
- Feed rate
- Moisture
- Sampling location
- Sample ID
- Mix timestamp

### D. Kiln / process data
- Timestamp
- Plant ID
- Kiln ID
- Kiln feed rate
- Kiln speed
- Burning zone temperature
- Calciner temperature
- Preheater temperatures
- O2
- CO
- CO2
- Fuel rate
- Fuel type
- Pressure
- Draft / back pressure
- Cooler conditions if available
- Sensor IDs and DCS/SCADA tags
- Sampling frequency

### E. Clinker chemistry
- Sample ID
- Batch ID
- Plant ID
- Kiln ID
- Sampling timestamp
- CaO, SiO2, Al2O3, Fe2O3, MgO, SO3, Na2O, K2O, Cl
- LOI or relevant chemistry
- Oxide measurement method
- Lab ID
- Analyst / instrument
- Data status

### F. Clinker phase measurements
- Sample ID
- Phase values for C3S, C2S, C3A, C4AF
- XRD / QXRD / Rietveld measurement method
- Instrument model
- Analysis date
- Lab ID
- Phase quantification uncertainty if available
- Data status

### G. Free CaO
- Sample ID
- Free CaO wt%
- ASTM / ISO-equivalent method
- Lab ID
- Measurement date
- Method reference
- Quality flag

### H. Sample identifiers
- Sample_ID
- Lab_Sample_ID
- Batch_ID
- Raw_Mix_ID
- Kiln_Run_ID
- Plant_ID
- Kiln_ID
- Line_ID
- Material_Lot_ID
- Source_ID

### I. Timestamps
- Raw material receipt / use time
- Raw mix timestamp
- Kiln feed timestamp
- Kiln process window start/end
- Clinker sampling time
- Lab analysis time
- Data extraction time

### J. Laboratory measurement methods
- XRF method
- XRD / QXRD / Rietveld method
- Free CaO method
- Instrument model
- Calibration details
- Reference standards used
- Detection limits if available

### K. Data provenance
- Source of data
- Plant or lab owner
- Data collection system
- Sampling method
- Sample handling notes
- Date/time of measurement
- Analyst / operator
- Data status (measured / calculated / synthetic / missing)
- Data dictionary

### L. Data-use / license permission
- Data ownership
- Research-use permission
- Internal / partner / public release status
- License or use agreement status
- Contact for approval and transfer

## Minimum practical dataset request

The minimum practical dataset for the research should include:
- plant and kiln metadata
- raw material chemistry with source and lot IDs
- raw mix or kiln-feed composition
- kiln time-series variables
- clinker sample IDs and measured chemistry
- measured phase values by XRD/Rietveld
- measured free CaO
- timestamps and production window information
- explicit measurement methods and provenance

## Important scientific constraints

- No Bogue-derived phase values may be used as ground truth.
- No synthetic labels or formula-generated targets may be supplied as the real target set.
- Any derived values must be clearly tagged as derived, not measured.
- All target values must be traceable to a real sample and lab method.

## Minimum acceptable status for future use

A dataset should only be considered for Step 12 after it contains a real sample-batch-process chain with valid IDs, timestamps, methods, and provenance.
