# Dataset Inventory

This audit covers the six datasets found in the project root:

- `DiB - Cement Plant data.xlsx`
- `Concrete_Data.xls`
- `blended_cement_concrete_database.csv`
- `slump_test.data`
- `slump_test.names`
- `Raw_Materials.xlsx`

## 1) `DiB - Cement Plant data.xlsx`

- Format: Excel workbook (.xlsx)
- Sheets: 3
  - `A. Inventory Data of Cement `
  - `B. Electricity Data and Impacts`
  - `C. Impact Assessment Results `
- Rows: approx. 510, 217, 399 respectively
- Columns: 6, 7, 6 respectively
- Observed structure: workbook appears to be a published case-study inventory / LCA appendix. It is not a standard plant telemetry export.
- Missing values: high; many rows are header/annotation rows; column names are generic `Unnamed: x` until parsed carefully.
- Duplicates: present in raw sheet structure because of repeated table headers and narrative rows.
- Likely targets: plant-level energy intensity, emissions, inventory balances, LCA impact outcomes.
- Likely inputs/features: material inputs, fuel inputs, transport distances, electricity usage, energy mix.
- Engineering purpose: life-cycle inventory / environmental assessment of cement plant operations.
- Units: kg, tonne, km, kWh, MJ/tonne, kgCO2/kWh, etc.; mostly process and LCA units.
- Provenance: appears to be a case-study workbook associated with a cement plant LCA / inventory study; not a direct industrial database export without a clear plant ID, date stamp, or canonical source metadata row.
- License: unknown from file metadata.

## 2) `Concrete_Data.xls`

- Format: Excel workbook (.xls)
- Sheets: 3
  - `Sheet1`
  - `Sheet2` (empty)
  - `Sheet3` (empty)
- Rows: 1030 in `Sheet1`
- Columns: 9 in `Sheet1`
- Variables: cement, blast furnace slag, fly ash, water, superplasticizer, coarse aggregate, fine aggregate, age, compressive strength.
- Units: kg/m^3 mixture, day, MPa.
- Missing values: none in `Sheet1`
- Duplicates: 25 duplicate rows in the raw file
- Likely target: concrete compressive strength (MPa)
- Likely features: component mix design + age
- Engineering purpose: concrete mix optimization and strength prediction
- Provenance: widely used concrete strength dataset; appears to be a standard design-mix dataset rather than a plant production dataset.
- License: unknown; typically treated as benchmark/open dataset but file metadata is not explicit.

## 3) `blended_cement_concrete_database.csv`

- Format: CSV
- Delimiter: comma
- Rows: 8,979
- Columns: 17
- Variables:
  - Cement (kg/m3)
  - Blast Furnace Slag (kg/m3)
  - Fly Ash (kg/m3)
  - Silica Fume (kg/m3)
  - Calcined Clay (kg/m3)
  - Limestone (kg/m3)
  - Water (kg/m3)
  - Superplasticizer (kg/m3)
  - Coarse Aggregate (kg/m3)
  - Fine Aggregate (kg/m3)
  - Age (day)
  - Compressive Strength (MPa)
  - Curing Temperature (°C)
  - Curing Humidity (%)
  - Aspect Ratio
  - Specimen Volume (mm3)
  - DOI
- Missing values: 10,602 cells missing across the dataset
- Duplicates: 80 rows duplicated
- Likely target: compressive strength of concrete/mortar specimens
- Likely features: mix proportions + environmental curing + specimen geometry
- Engineering purpose: cement and concrete formulation research; generalized strength modeling
- Units: kg/m3, day, MPa, °C, %, mm3, DOI reference
- Provenance: literature-derived concrete database; includes DOI references and mixes from multiple publications.
- License: unknown; dataset is a compiled bibliographic aggregate and should be treated as research data, not a single plant dataset.

## 4) `slump_test.data`

- Format: CSV/flat table (.data)
- Delimiter: comma
- Rows: 103 data rows + header
- Columns: 11 including header
- Variables:
  - No
  - Cement
  - Slag
  - Fly ash
  - Water
  - SP
  - Coarse Aggr.
  - Fine Aggr.
  - SLUMP(cm)
  - FLOW(cm)
  - Compressive Strength (28-day)(Mpa)
- Units: kg/m3 for ingredients; cm for slump/flow; MPa for strength
- Missing values: none
- Duplicates: none
- Likely targets: slump, flow, 28-day compressive strength
- Likely features: cementitious composition and aggregate proportions
- Engineering purpose: concrete workability and strength prediction
- Provenance: UCI / Yeh concrete dataset.
- License: usually provided as benchmark research data; not explicitly declared in the file.

## 5) `slump_test.names`

- Format: dataset description / metadata file
- Rows: not tabular; documentation for `slump_test.data`
- Purpose: describes source, attributes, tasks, and literature references
- Provenance: UCI/Chung-Hua University; donor I-Cheng Yeh
- License: not specified in file

## 6) `Raw_Materials.xlsx`

- Format: Excel workbook (.xlsx)
- Sheets: 1 (`Raw_Materials`)
- Rows: 6
- Columns: 26
- Variables include:
  - Sample_ID
  - Material_Type
  - Source_ID
  - Sample_Name
  - CaO, SiO2, Al2O3, Fe2O3, MgO, SO3, Na2O, K2O, TiO2, P2O5, MnO, LOI
  - Moisture
  - Particle_Size
  - Fineness
  - Specific_Surface_Area
  - Mineralogy
  - XRF_Method
  - Value_Status
  - Source_Page_Table
  - DOI_or_URL
  - Notes
- Units: oxide % by mass, LOI %, moisture %, particle size, fineness, specific surface area (depends on reported method)
- Missing values: notable; many chemistry columns are NaN for non-applicable materials
- Duplicates: none
- Likely target: material characterization; derived raw-mix blend design support
- Likely features: oxide composition and material-specific descriptors
- Engineering purpose: raw material chemistry database for raw mix design and chemistry checks
- Provenance: described as measured/reported data with DOI and source table metadata; appears more like a curated sample database than a large plant production log.
- License: unknown

## Summary of dataset roles

- `Raw_Materials.xlsx`: raw material chemistry knowledge base
- `Concrete_Data.xls`: concrete strength benchmark dataset
- `blended_cement_concrete_database.csv`: broad literature-based blended concrete strength dataset
- `slump_test.data` + `slump_test.names`: concrete workability / strength dataset
- `DiB - Cement Plant data.xlsx`: LCA / plant inventory case-study document, not a clean process dataset

## Immediate conclusion

There is no single master dataset that covers `Raw Material -> Raw Mix -> Raw Meal -> Kiln -> Clinker -> Cement -> Concrete` in one coherent table. The available datasets are fragmented and have no reliable cross-dataset ID system across the whole chain.
