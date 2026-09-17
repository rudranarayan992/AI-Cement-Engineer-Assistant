# Schema Map

This schema map organizes variables from the available datasets into the cement production and concrete lifecycle categories used by the architecture.

## RAW MATERIALS

From `Raw_Materials.xlsx`:

- `Sample_ID`
- `Material_Type`
- `Source_ID`
- `Sample_Name`
- `CaO`, `SiO2`, `Al2O3`, `Fe2O3`, `MgO`, `SO3`, `Na2O`, `K2O`, `TiO2`, `P2O5`, `MnO`, `LOI`
- `Moisture`
- `Particle_Size`
- `Fineness`
- `Specific_Surface_Area`
- `Mineralogy`
- `XRF_Method`
- `Value_Status`
- `Source_Page_Table`
- `DOI_or_URL`
- `Notes`

## RAW MIX

Relevant in concrete datasets and derived blend design contexts:

- `Cement (kg/m3)`
- `Blast Furnace Slag (kg/m3)`
- `Fly Ash (kg/m3)`
- `Silica Fume (kg/m3)`
- `Calcined Clay (kg/m3)`
- `Limestone (kg/m3)`
- `Coarse Aggregate (kg/m3)`
- `Fine Aggregate (kg/m3)`
- `Water (kg/m3)`
- `Superplasticizer (kg/m3)`

Also present in `slump_test.data`:

- `Cement`, `Slag`, `Fly ash`, `Water`, `SP`, `Coarse Aggr.`, `Fine Aggr.`

## RAW MEAL CHEMISTRY

Not directly available in a single canonical table. The closest raw chemistry is in `Raw_Materials.xlsx` and may support raw meal blending calculations if converted to a blend recipe.

Possible generated features:

- weighted oxide composition by mass fraction
- loss on ignition (LOI)
- moisture-adjusted chemistry
- combined raw-mix oxide balance

## LSF

Not directly measured in the raw datasets.

Derived only if the relevant oxides are available from a raw meal or clinker chemistry dataset, typically using:

- `CaO`, `SiO2`, `Al2O3`, `Fe2O3`
- `LSF = CaO / (2.8*SiO2 + 1.18*Al2O3 + 0.65*Fe2O3)`

This is a derived engineering variable, not an original column in the provided data.

## SM

Derived engineering variable:

- `SM = SiO2 / (Al2O3 + Fe2O3)`

## AM

Derived engineering variable:

- `AM = Al2O3 / Fe2O3`

## KILN PROCESS

The `DiB - Cement Plant data.xlsx` workbook contains process- and LCA-oriented operational information, especially in the electricity and inventory sheets, including:

- fuel use
- electricity generation or use
- transport distances
- material amounts
- system energy / thermal energy use

But it does not provide a clean kiln telemetry table with time series.

## CLINKER CHEMISTRY

Not directly available as a canonical clinker chemistry table.

Potentially reconstructable only from a separate raw meal or clinker process dataset, which is not present.

## C3S

Not directly available in any dataset.

This is generally Bogue-derived; it should be treated as a model output or engineered variable, not as a raw measured variable.

## C2S

Not directly available in any dataset.

## C3A

Not directly available in any dataset.

## C4AF

Not directly available in any dataset.

## FREE CaO

Not directly provided in any available dataset.

This is a kiln-quality metric and would normally require clinker chemistry or laboratory analysis.

## CEMENT QUALITY

Relevant variables from concrete and workability datasets:

- `Compressive Strength (MPa)`
- `Age (day)`
- `Curing Temperature (°C)`
- `Curing Humidity (%)`
- `Specimen Volume (mm3)`
- `Aspect Ratio`

Available concrete datasets do not include cement manufacturing quality metrics such as:

- clinker phase fractions
- free CaO
- Blaine fineness
- set time
- soundness

## CONCRETE / MORTAR

From concrete datasets:

- `Concrete compressive strength(MPa, megapascals)`
- `Compressive Strength (MPa)`
- `SLUMP(cm)`
- `FLOW(cm)`
- `Age (day)`
- mix proportions (cement, slag, fly ash, aggregates, water, superplasticizer)

## ENVIRONMENTAL / LCA

From `DiB - Cement Plant data.xlsx`:

- raw-material amounts
- transport distances and modes
- fuel use
- electricity generation / impacts
- energy inputs
- MJ/tonne and kgCO2 emissions indicators
- impact assessment results categories

## Cross-dataset mapping summary

| Category | Datasets with material | Notes |
|---|---|---|
| Raw materials | `Raw_Materials.xlsx` | best raw chemistry reference |
| Raw mix | `Concrete_Data.xls`, `slump_test.data`, `blended_cement_concrete_database.csv` | concrete mixture formulations |
| Raw meal chemistry | none canonical | must be inferred or absent |
| LSF/SM/AM | none direct | derived only if oxide chemistry exists |
| Kiln process | `DiB - Cement Plant data.xlsx` (partial) | inventory-level, not time-series |
| Clinker chemistry | none direct | absent |
| C3S/C2S/C3A/C4AF | none direct | requires Bogue or lab data |
| Free CaO | none direct | absent |
| Cement quality | not directly available | missing lineage from clinker to cement |
| Concrete / mortar | `Concrete_Data.xls`, `slump_test.data`, `blended_cement_concrete_database.csv` | best concrete target datasets |
| Environmental / LCA | `DiB - Cement Plant data.xlsx` | separate case-study inventory |
