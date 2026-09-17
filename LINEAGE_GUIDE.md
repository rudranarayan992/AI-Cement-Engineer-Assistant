# Cement Production Lineage & Traceability System

## Overview

This system establishes a **connected data chain** that traces cement strength back to its raw material origins:

```
Raw_Materials → Raw_Mix → Kiln_Process → Clinker → Cement → Strength_Test → Standards
                  ↓           ↓              ↓         ↓           ↓
            (composition)  (quality     (phase      (fineness) (performance)
                           indices)     composition)
```

Each stage is connected via **unique IDs**, enabling complete traceability and explainability.

## Data Model: The Connected Chain

### 1. Raw_Materials (`RawMaterial`)
**What:** Individual raw material sources
- Limestone, silica sand, clay, iron ore, gypsum, etc.
- **Key Properties:**
  - `raw_material_id`: Unique identifier
  - Oxide composition: CaO%, SiO2%, Al2O3%, Fe2O3%, MgO%
  - Physical properties: fineness, moisture, density
  - Source tracking: source, lot_number, date_acquired

**Example:**
```python
limestone = RawMaterial(
    raw_material_id="RM_001",
    name="Limestone",
    material_type="limestone",
    cao_percent=52.0,
    sio2_percent=2.5,
    source="Quarry A",
    lot_number="L202301"
)
```

### 2. Raw_Mix (`RawMix`)
**What:** A blend of raw materials (raw meal)
- Combines multiple raw materials in specific proportions
- **Linked to:** Raw_Materials (many-to-many via proportions)
- **Key Properties:**
  - `raw_mix_id`: Unique identifier
  - Resulting oxide composition (calculated from inputs)
  - **Quality indices:**
    - **LSF (Lime Saturation Factor)**: Controls phase formation
      - Typical range: 0.95–1.05 for OPC
      - Too low → too much free lime → poor durability
      - Too high → insufficient silica → weak early strength
    - **SM (Silica Modulus)**: SiO2/(Al2O3+Fe2O3)
      - Typical range: 2.3–3.0
      - Controls belite/aluminate balance
    - **AM (Alumina Modulus)**: Al2O3/Fe2O3
      - Typical range: 2–3
      - Controls ferrite formation

**Example Flow:**
```
Limestone (70%)  ─┐
Silica Sand (20%)─┼─→ Raw_Mix → CaO:50%, SiO2:30%, LSF:1.0, SM:2.7
Clay (10%)       ─┘
```

### 3. Kiln_Process (`KilnRun`)
**What:** A single kiln firing/clinkerization run
- Converts raw mix into clinker through high-temperature heating
- **Linked to:** Raw_Mix
- **Key Process Parameters:**
  - `kiln_run_id`: Unique identifier
  - `maximum_temperature_celsius`: 1450–1500°C typical
  - `dwell_time_minutes`: Time at peak temperature
  - `cooling_rate_celsius_per_hour`: Affects phase formation
  - Gas composition: CO2%, O2%, air/fuel ratio
  - Flame appearance, dust level (operational quality)

**Impact on Strength:**
- Higher temperature → more C3S (alite) → stronger cement
- Proper dwell time → better clinker burnability
- Rapid cooling → better phase stability

### 4. Clinker (`Clinker`)
**What:** The primary product after kiln firing
- Intermediate product ground to make cement
- **Linked to:** KilnRun, RawMix (backward traceability)
- **Key Properties:**
  - `clinker_id`: Unique identifier
  - **Phase composition (determines strength):**
    - **C3S (Alite)**: 3CaO·SiO2
      - 50–70% typical
      - **Drives early strength (1–28 days)**
      - Higher C3S → higher early strength
    - **C2S (Belite)**: 2CaO·SiO2
      - 15–30% typical
      - Drives late strength (after 28 days)
    - **C3A (Aluminate)**: 3CaO·Al2O3
      - 5–12% typical
      - Reacts very quickly, can cause false set
    - **C4AF (Ferrite)**: 4CaO·Al2O3·Fe2O3
      - 5–15% typical
      - Contributes less to strength
  - **Free CaO:** Uncombined calcium oxide
    - Should be <2.5%
    - High free CaO → durability issues, volume expansion
  - Quality rating: "premium", "standard", "reprocess"

**Critical Connection to Strength:**
```
High C3S (60–70%) → Higher 28-day strength
Low free CaO (<1.5%) → Better durability
Good fineness → Faster hydration
```

### 5. Cement (`CementBatch`)
**What:** Finished cement product (ground clinker + additives)
- Clinker ground to fine powder + gypsum (5%) + optional additives
- **Linked to:** Clinker (one-to-many: one clinker can make multiple cement batches)
- **Key Properties:**
  - `cement_batch_id`: Unique identifier
  - Composition:
    - Clinker: 90–95%
    - Gypsum: 3–5% (controls setting time)
    - Pozzolan/slag/fillers: 0–15% (optional)
  - **Fineness** (cm²/g):
    - 2500–4000 cm²/g typical
    - Higher fineness → higher early strength but higher water demand
    - Too fine → increases cost and water needs
  - Cement type: OPC, PPC, PSC, SRC, etc.

**Impact on Strength:**
```
C3S content (from clinker) + Fineness (from grinding) + W/C ratio → 28-day strength
```

### 6. Strength_Test (`StrengthTest`)
**What:** Concrete performance testing
- Tests concrete made with the cement
- **Linked to:** CementBatch, Clinker, RawMix (full backward trace)
- **Key Properties:**
  - `strength_test_id`: Unique identifier
  - Concrete mix design:
    - Cement: typically 400–500 kg/m³
    - **W/C ratio**: 0.35–0.65
      - Lower W/C → higher strength but less workability
      - ~0.45 is typical for good balance
    - Sand, gravel, water proportions
  - **Strength results:**
    - 7-day strength (early strength indicator)
    - **28-day strength** (design strength reference)
    - 90-day strength (long-term performance)
    - Flexural strength (optional)
  - Curing type: water, air, steam
  - Test standard: ASTM C39, IS 516, EN 12390, etc.

**Example Results:**
```
W/C 0.45, good cement → 45–50 MPa at 28 days
W/C 0.55, same cement → 35–40 MPa at 28 days
```

### 7. Standards (`StandardCompliance`)
**What:** Compliance verification against specifications
- **Linked to:** CementBatch, StrengthTest
- Checks: fineness, strength, expansion, setting time, etc.
- Status: "passed", "failed", "conditional"

### 8. ML_Training (`LineageTrace`)
**What:** Complete end-to-end trace for ML models
- Combines all stages into one searchable record
- Enables: "Explain why this cement has 45 MPa strength"

---

## The Connected Database Schema

### Tables & Relationships

```
raw_materials
    ↓
    │ (many-to-many via raw_mix_composition)
    ↓
raw_mixes
    ↓
    ├─→ kiln_runs
    │       ↓
    │   clinkers
    │       ↓
    │   cement_batches
    │       ↓
    │   strength_tests
    │       ↓
    │   standards_compliance
    │
    ├─→ clinkers (can be ground into multiple cement batches)
    └─→ strength_tests (each cement in multiple tests)
```

### Foreign Keys (The Connections)

| Table | Foreign Keys | Meaning |
|-------|--------------|---------|
| `raw_mixes` | — | Starting point |
| `kiln_runs` | `raw_mix_id` | Which raw meal was fired? |
| `clinkers` | `kiln_run_id`, `raw_mix_id` | Which kiln run? Which raw mix? |
| `cement_batches` | `clinker_id`, `kiln_run_id`, `raw_mix_id` | Which clinker? Full trace. |
| `strength_tests` | `cement_batch_id`, `clinker_id`, `kiln_run_id`, `raw_mix_id` | Full backward trace |
| `standards_compliance` | `cement_batch_id`, `strength_test_id` | Which test/batch? |

---

## Working with the System

### 1. Creating the Data Chain

```python
from src.data_chain_loader import DataChainBuilder

builder = DataChainBuilder(db_path="cement_lineage.db")

# 1. Define raw materials
limestone = RawMaterial(raw_material_id="RM_001", name="Limestone", cao_percent=52.0, ...)
sand = RawMaterial(raw_material_id="RM_002", name="Silica Sand", sio2_percent=92.0, ...)

# 2. Create raw mix from proportions
raw_mix = builder.create_raw_mix_from_materials(
    raw_mix_id="RM_001",
    material_proportions={"RM_001": 70.0, "RM_002": 30.0},
    materials={"RM_001": limestone, "RM_002": sand}
)
# → Automatically calculates LSF, SM, AM

# 3. Create kiln run
kiln_run = builder.create_kiln_run(
    kiln_run_id="KR_001",
    raw_mix_id=raw_mix.raw_mix_id,
    maximum_temperature_celsius=1480,
    ...
)

# 4. Create clinker with measured phase composition
clinker = builder.create_clinker(
    clinker_id="CK_001",
    kiln_run_id=kiln_run.kiln_run_id,
    raw_mix_id=raw_mix.raw_mix_id,
    c3s_percent=65.0,  # Measured from X-ray diffraction
    free_cao_percent=1.5,
    ...
)

# 5. Create cement batch
cement = builder.create_cement_batch(
    cement_batch_id="CB_001",
    clinker_id=clinker.clinker_id,
    kiln_run_id=kiln_run.kiln_run_id,
    raw_mix_id=raw_mix.raw_mix_id,
    fineness_cm2_g=3500,
    ...
)

# 6. Create strength test with full backward links
test = builder.create_strength_test(
    strength_test_id="ST_001",
    cement_batch_id=cement.cement_batch_id,
    clinker_id=clinker.clinker_id,
    kiln_run_id=kiln_run.kiln_run_id,
    raw_mix_id=raw_mix.raw_mix_id,
    compressive_strength_28d_mpa=45.0,
    w_c_ratio=0.45,
    ...
)
```

### 2. Querying the Lineage Chain

```python
from src.data_integration import LineageDatabase

db = LineageDatabase("cement_lineage.db")

# Get complete chain for a cement batch
chain = db.get_lineage_chain("CB_001")

print(f"Raw materials: {[m['name'] for m in chain['raw_materials']]}")
print(f"Raw mix LSF: {chain['raw_mix']['lsf']:.2f}")
print(f"Kiln temp: {chain['kiln_run']['max_temp_celsius']}°C")
print(f"Clinker C3S: {chain['clinker']['c3s_percent']:.1f}%")
print(f"Cement fineness: {chain['cement']['fineness_cm2_g']} cm²/g")
print(f"28-day strength: {chain['strength_tests'][0]['strength_28d_mpa']:.1f} MPa")
```

### 3. Explaining Strength Results

```python
from src.explainability.strength_explainer import StrengthExplainer
from src.data_lineage import LineageTrace

# Create a lineage trace from data
trace = LineageTrace()
# ... populate with data from database or files ...

# Create explainer
explainer = StrengthExplainer(trace)

# Generate causal explanation
explanation = explainer.explain_strength_result(observed_strength_mpa=45.0)
print(explanation)

# Example output:
# ======================================================================
# CEMENT STRENGTH CAUSALITY ANALYSIS
# ======================================================================
#
# Observed 28-day Strength: 45.0 MPa
#
# Contributing Factors:
# ✓ POSITIVE FACTORS (increase strength):
#   • clinker_c3s: 65.0 % (✓ Normal) - ↑ increases strength
#   • cement_fineness: 3500.0 cm²/g (✓ Normal) - ↑ increases strength
#
# ✗ NEGATIVE FACTORS (decrease strength):
#   • concrete_w_c_ratio: 0.45  (✓ Normal) - ↓ decreases strength
#
# ======================================================================
# CAUSAL CHAIN NARRATIVE
# ======================================================================
#
# 1. RAW MATERIAL SELECTION
# ----------------------------------------
#   • Limestone (limestone)
#     CaO: 52.0%, SiO2: 2.5%
#
#   → Raw mix LSF: 1.00 (✓ Good)
#     Effect: Controls phase composition and burnability
#
# 2. KILN PERFORMANCE & CLINKERIZATION
# ----------------------------------------
#   • Maximum temperature: 1480°C
#     ✓ Within spec - optimal phase formation
#
#   • Clinker alite (C3S) content: 65.0%
#     ✓ High alite - STRONG early strength expected
#
# 3. CEMENT GRINDING & COMPOSITION
# ----------------------------------------
#   • Cement fineness: 3500 cm²/g
#     ✓ High fineness - INCREASED hydration rate
#   • Cement type: OPC
#
# 4. CONCRETE PROPERTIES & CURING
# ----------------------------------------
#   • Water-cement ratio: 0.45
#     ✓ Low W/C - HIGH strength expected
#   • Curing type: water
#
# 5. RESULTING STRENGTH
# ----------------------------------------
#    The combination of:
#    • Alite content (from raw mix & kiln temperature)
#    • Cement fineness (from grinding)
#    • Water-cement ratio (from concrete design)
#    • Curing conditions
#    → Determines final 28-day compressive strength
```

### 4. Getting Recommendations

```python
# Get recommendations to improve strength
recommendations = explainer.get_recommendations()
for rec in recommendations:
    print(f"⚠ {rec}")

# Example:
# ⚠ LSF is too low (0.92): Increase limestone content or decrease silica
# ⚠ Kiln temperature (1420°C) is outside ideal range: Adjust fuel rate or kiln speed
# ⚠ Cement is too coarse (2200 cm²/g): Increase grinding time
```

### 5. Comparing Two Cement Batches

```python
from src.explainability.strength_explainer import compare_cement_batches

comparison = compare_cement_batches(trace1, trace2)
print(comparison)
```

---

## For ML Training

### Feature Engineering Pipeline

The lineage system enables powerful feature engineering:

1. **Raw Material Features:**
   - Individual oxide percentages from each material
   - Material type (encoded)
   - Fineness, moisture, density

2. **Raw Mix Features:**
   - Aggregate oxide composition
   - LSF, SM, AM (quality indices)
   - Proportion of each material type

3. **Kiln Features:**
   - Maximum temperature
   - Dwell time, cooling rate
   - Gas composition
   - Operational indicators (flame, dust)

4. **Clinker Features:**
   - Phase composition: C3S, C2S, C3A, C4AF
   - Free CaO
   - Fineness, density

5. **Cement Features:**
   - Clinker %, gypsum %, additives %
   - Fineness, density
   - Cement type (encoded)

6. **Concrete Features:**
   - W/C ratio
   - Cement content, water content
   - Aggregate proportions
   - Curing type (encoded)

### Training Set Construction

```python
from src.data_integration import LineageDatabase

db = LineageDatabase("cement_lineage.db")

# Query all cement batches with strength tests
training_data = []
for cement_batch_id in db.get_all_cement_batches():
    chain = db.get_lineage_chain(cement_batch_id)
    
    # Extract features
    features = {
        # Raw materials
        "rm_cao_avg": mean([m["cao_percent"] for m in chain["raw_materials"]]),
        "rm_sio2_avg": mean([m["sio2_percent"] for m in chain["raw_materials"]]),
        # Raw mix
        "raw_mix_lsf": chain["raw_mix"]["lsf"],
        "raw_mix_sm": chain["raw_mix"]["sm"],
        # Kiln
        "kiln_temp": chain["kiln_run"]["max_temp_celsius"],
        # Clinker
        "clinker_c3s": chain["clinker"]["c3s_percent"],
        "clinker_free_cao": chain["clinker"]["free_cao_percent"],
        # Cement
        "cement_fineness": chain["cement"]["fineness_cm2_g"],
        # Concrete
        "w_c_ratio": chain["strength_tests"][0]["w_c_ratio"],
    }
    
    # Target
    target = chain["strength_tests"][0]["strength_28d_mpa"]
    
    training_data.append((features, target))

# Now train your XGBoost model with full traceability!
```

---

## Benefits of This System

1. **Complete Traceability:** Track every cement from raw material origin to strength result
2. **Explainability:** Explain strength variations based on production history
3. **Root Cause Analysis:** "Why did this batch have lower strength?"
   - Check LSF of raw mix
   - Check C3S content of clinker
   - Check fineness of cement
   - Check W/C ratio of concrete
4. **Quality Control:** Identify which production stage caused quality issues
5. **ML Model Interpretability:** Features have physical meaning (not just "X17")
6. **Process Optimization:** Understand impact of each process parameter
7. **Standards Compliance:** Full audit trail for certification

---

## Database Files

- `cement_lineage.db`: SQLite database with all connected data
- Auto-created with schema on first use
- Tables: raw_materials, raw_mixes, raw_mix_composition, kiln_runs, clinkers, cement_batches, strength_tests, standards_compliance

## Next Steps

1. Load your existing data into the connected schema
2. Use `DataChainBuilder` to populate the database
3. Train ML models with full traceability
4. Use `StrengthExplainer` to generate insights
5. Continuously add new production batches and tests

This ensures every prediction model can trace: **"This cement has lower strength because this raw-material combination produced lower alite, which resulted from this kiln temperature and this clinker quality."**
