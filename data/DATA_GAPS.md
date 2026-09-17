# Data Gaps for the Full Cement-to-Concrete Chain

The available datasets cover fragments of the production chain, but they do not form a complete end-to-end dataset from raw materials to final concrete performance.

## 1) Raw Material -> Raw Mix

Missing / weakly represented:

- plant-specific blend proportions for a real kiln feed
- time-stamped raw mix recipe records
- feed ratio tracking by quarry / mine / material lot
- moisture and variability by material batch

Current coverage:

- `Raw_Materials.xlsx` provides material chemistry for a small set of materials.
- Concrete datasets show mix designs, but they are concrete recipes, not raw-mix recipes feeding a kiln.

## 2) Raw Mix -> Raw Meal

Missing:

- raw meal chemistry after blending
- kiln feed chemistry at the mill exit
- preheater/precalciner operating conditions
- raw meal fineness and moisture control
- blend optimization records

Current coverage:

- only approximate chemical values for individual raw materials, not a complete, time-linked raw meal composition table.

## 3) Raw Meal -> Kiln

Missing:

- kiln feed rate and residence time
- temperature profiles by zone
- fuel composition and excess air
- burner settings
- kiln rotation / speed / CO / O2 / NOx / SOx logs
- fuel-specific thermal input

Current coverage:

- `DiB - Cement Plant data.xlsx` includes some energy and transport inventory data, but not a production-equivalent kiln telemetry table.

## 4) Kiln -> Clinker

Missing:

- clinker chemistry by production batch
- clinker phase fractions (C3S, C2S, C3A, C4AF)
- free CaO
- clinker grindability / fineness
- thermal profile and burnability metrics

Current coverage:

- no direct clinker chemistry dataset is present.
- no Bogue-derived phase table is supplied.

Critical Step 9C finding:

- The current `clinker_analysis.csv` in the repo contains generated formula outputs such as `Free_CaO_pct`, `C3S_pct`, `C2S_pct`, `C3A_pct`, and `C4AF_pct`.
- These values are produced in `scripts/generate_cement_dataset.py` using deterministic chemistry formulas and synthetic noise, not measured XRD / lab mineralogy.
- Therefore the available phase and free-CaO targets are not legitimate ground-truth labels for real clinker model training.

## 5) Clinker -> Cement

Missing:

- cement chemical composition after blending with gypsum / SCMs
- cement fineness (Blaine, residue)
- setting time and soundness
- strength activity index
- mill operating data

Current coverage:

- none of these are available as a direct empirical cement production dataset.

Critical Step 9C finding:

- The `cement_quality.csv` values such as `Strength_3d_MPa`, `Strength_7d_MPa`, and `Strength_28d_MPa` are also generated from formulaic relationships in `scripts/generate_cement_dataset.py`.
- These are synthetic proxy outputs rather than measured cement lab strengths from a plant or lab program.

## 6) Cement -> Concrete

Missing:

- actual cement plant cement batches linked to concrete production
- batching logs from a specific concrete plant
- slump / flow / strength measured on the same concrete mix design over time

Current coverage:

- concrete datasets exist, but they are independent recipe datasets rather than traceable cement-plant outputs.

## 7) Data provenance / linkage gaps

No reliable join keys across chain stages:

- no common `Plant_ID`
- no consistent `Sample_ID`
- no `Batch_ID`
- no `Mix_ID` connecting raw materials to kiln or cement to concrete
- no `Date`/`Time` series that align across datasets
- no matching publication / DOI metadata across all tables

## 8) Required minimum information for a complete chain

To build a legitimate cement-production-to-concrete chain, the project would need at minimum:

- raw material lot IDs and measured chemistry
- raw mix recipe by date/batch
- raw meal chemistry after blending
- process operation logs for kiln and cooler
- clinker chemistry and free CaO measured by lab analysis
- clinker phase fractions from XRD / QXRD or equivalent
- cement chemistry and fineness
- concrete mix recipe and age-specific strength measurements from the same cement batch

Without these, the data cannot be legally or scientifically linked into a single causal chain.

## 9) Step 9C conclusion: why the current cement chain is not trainable as a real ML system

The project contains a synthetic cement chain generated from formulas, not a measured industrial dataset.

This means the repository cannot support a legitimate model for:

- `Free_CaO` prediction as a real measured target
- clinker phase prediction (`C3S`, `C2S`, `C3A`, `C4AF`) from measured XRD labels
- production cement-strength prediction from measured plant data

A legitimate ML project requires measured labels, not formula-derived placeholders. Without lab-measured clinker mineralogy, free CaO, and plant quality data, training on the current chain would effectively learn the generator equations instead of the underlying industrial process.
