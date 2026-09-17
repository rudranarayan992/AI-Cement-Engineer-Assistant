# Connected Data Chain Architecture

## Quick Summary

Your dataset is now organized as a **connected chain** that enables full traceability and explainability:

```
Raw_Materials → Raw_Mix → Kiln_Process → Clinker → Cement → Strength_Test
     ↓              ↓            ↓           ↓        ↓          ↓
  (sourced)    (blended)    (fired)    (measured)  (ground)  (tested)
```

Each stage has **unique IDs** linking back to previous stages, enabling queries like:
- "Why does this cement have 45 MPa strength?"
- "This raw material combination produced lower alite..."
- "Which process parameter caused the issue?"

---

## Files Added

### Core Data Models
1. **[src/data_lineage.py](src/data_lineage.py)** - Data classes for each stage
   - `RawMaterial`, `RawMix`, `KilnRun`, `Clinker`, `CementBatch`, `StrengthTest`, `StandardCompliance`
   - `LineageTrace` - Complete end-to-end trace
   - Each class has properties and methods to calculate quality indices (LSF, SM, AM, etc.)

2. **[src/data_integration.py](src/data_integration.py)** - Database layer
   - `LineageDatabase` - SQLite wrapper with full schema
   - Methods to save/load each stage
   - Queries to retrieve complete lineage chains
   - Foreign keys connecting all stages

3. **[src/data_chain_loader.py](src/data_chain_loader.py)** - Data loading utilities
   - `DataChainBuilder` - Helper to construct the chain from data files
   - Methods to create each stage with automatic ID generation
   - CSV loader for raw materials
   - Example script showing end-to-end chain creation

4. **[src/explainability/strength_explainer.py](src/explainability/strength_explainer.py)** - Causality analysis
   - `StrengthExplainer` - Explains strength results based on lineage
   - Generates natural language explanations
   - Identifies key factors and their impact
   - Provides recommendations for improvement
   - Ranks factors by importance

### Documentation
5. **[LINEAGE_GUIDE.md](LINEAGE_GUIDE.md)** - Comprehensive guide
   - What each stage represents
   - Why the connections matter
   - How to use the system
   - Examples and code snippets
   - Benefits and use cases

6. **[DATA_CHAIN_README.md](DATA_CHAIN_README.md)** - This file

### Examples
7. **[example_lineage_demo.py](example_lineage_demo.py)** - Complete working example
   - Creates all stages: raw materials → cement → strength test
   - Demonstrates traceability queries
   - Shows causality explanation in action
   - Run it to see the system work

---

## Database Schema

Automatically created in `cement_lineage.db`:

```
raw_materials
  └─→ raw_mix_composition (junction table)
  └─→ raw_mixes
        └─→ kiln_runs
              └─→ clinkers
                    └─→ cement_batches
                          └─→ strength_tests
                          └─→ standards_compliance
```

### Key Tables

| Table | Purpose | Foreign Keys |
|-------|---------|--------------|
| `raw_materials` | Raw material sources | None (starting point) |
| `raw_mix_composition` | Links materials to mix (many-to-many) | raw_mix_id, raw_material_id |
| `raw_mixes` | Raw meal blends with quality indices | None |
| `kiln_runs` | Kiln firing records | raw_mix_id |
| `clinkers` | Clinker products with phase composition | kiln_run_id, raw_mix_id |
| `cement_batches` | Ground cement with additives | clinker_id, kiln_run_id, raw_mix_id |
| `strength_tests` | Concrete strength results | cement_batch_id, clinker_id, kiln_run_id, raw_mix_id |
| `standards_compliance` | Standard compliance checks | cement_batch_id, strength_test_id |

---

## Getting Started

### 1. Run the Example

```bash
cd AI_Cement_Project
python example_lineage_demo.py
```

This will:
- Create a complete data chain (raw materials through strength test)
- Save it to `cement_lineage_demo.db`
- Query the chain to show traceability
- Explain the strength result (48.2 MPa)
- Show factors contributing to strength
- Print recommendations

### 2. Load Your Existing Data

```python
from src.data_chain_loader import DataChainBuilder
from src.data_lineage import RawMaterial

# Create builder
builder = DataChainBuilder(db_path="my_cement_data.db")

# Load raw materials from CSV
materials = builder.load_raw_materials_from_csv("raw_materials.csv")

# Or create manually
limestone = RawMaterial(
    raw_material_id="RM_001",
    name="Limestone",
    material_type="limestone",
    cao_percent=52.0,
    sio2_percent=2.5,
    # ... other properties
)
builder.db.save_raw_material(limestone)

# Create raw mix
raw_mix = builder.create_raw_mix_from_materials(
    raw_mix_id="RM_001",
    material_proportions={"RM_001": 70.0, "RM_002": 20.0, "RM_003": 10.0},
    materials={"RM_001": limestone, "RM_002": sand, "RM_003": clay}
)
# → Automatically calculates LSF, SM, AM

# Create kiln run
kiln = builder.create_kiln_run(
    kiln_run_id="KR_001",
    raw_mix_id=raw_mix.raw_mix_id,
    maximum_temperature_celsius=1480,
    # ... other params
)

# Create clinker
clinker = builder.create_clinker(
    clinker_id="CK_001",
    kiln_run_id=kiln.kiln_run_id,
    raw_mix_id=raw_mix.raw_mix_id,
    c3s_percent=65.0,
    free_cao_percent=1.2,
    # ... other params
)

# Create cement
cement = builder.create_cement_batch(
    cement_batch_id="CB_001",
    clinker_id=clinker.clinker_id,
    kiln_run_id=kiln.kiln_run_id,
    raw_mix_id=raw_mix.raw_mix_id,
    fineness_cm2_g=3500,
    # ... other params
)

# Create strength test
test = builder.create_strength_test(
    strength_test_id="ST_001",
    cement_batch_id=cement.cement_batch_id,
    clinker_id=clinker.clinker_id,
    kiln_run_id=kiln.kiln_run_id,
    raw_mix_id=raw_mix.raw_mix_id,
    w_c_ratio=0.45,
    compressive_strength_28d_mpa=45.0,
    # ... other params
)
```

### 3. Query and Explain

```python
from src.data_integration import LineageDatabase
from src.explainability.strength_explainer import StrengthExplainer
from src.data_lineage import LineageTrace

# Query database
db = LineageDatabase("my_cement_data.db")
chain = db.get_lineage_chain("CB_001")

# Build trace
trace = LineageTrace()
# ... populate from database or files ...

# Explain strength
explainer = StrengthExplainer(trace)
explanation = explainer.explain_strength_result(observed_strength_mpa=45.0)
print(explanation)

# Get recommendations
recommendations = explainer.get_recommendations()
for rec in recommendations:
    print(f"⚠ {rec}")
```

---

## Key Concepts

### Quality Indices

These are calculated at the raw mix stage and tracked through production:

1. **LSF (Lime Saturation Factor)** = CaO / (2.8×SiO2 + 1.18×Al2O3 + 0.65×Fe2O3)
   - Target: 0.95–1.05 for OPC
   - Controls phase formation and clinker reactivity
   - LSF < 0.95: Too much silica → weak cement
   - LSF > 1.05: Too much lime → durability issues

2. **SM (Silica Modulus)** = SiO2 / (Al2O3 + Fe2O3)
   - Target: 2.3–3.0
   - Controls the ratio of belite to aluminate phases

3. **AM (Alumina Modulus)** = Al2O3 / Fe2O3
   - Target: 2.0–3.0
   - Controls ferrite formation

### Phase Composition (in Clinker)

These are determined by raw mix composition and kiln conditions:

- **C3S (Alite)**: 3CaO·SiO2
  - 50–70% typical
  - **Drives early strength** (1–28 days)
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

- **Free CaO**: Uncombined calcium oxide
  - Should be <2.5%
  - High free CaO → durability issues, volume expansion

### Cement Fineness

Measured in cm²/g (Blaine fineness):
- 2500–4000 cm²/g typical
- Higher fineness → faster hydration → higher early strength
- Trade-off: higher fineness requires more grinding energy and water

### Water-Cement Ratio (W/C)

In concrete:
- 0.35–0.45: High strength, low workability
- 0.45–0.55: Balanced
- 0.55–0.65: Lower strength, higher workability

---

## Traceability Example

```
Raw Materials Selected:
├─ Limestone (70%): CaO=52%
├─ Silica Sand (20%): SiO2=92%
└─ Clay (10%): Al2O3=22%
         ↓
Raw Mix Created:
├─ CaO: 50%
├─ SiO2: 32%
├─ LSF: 1.00 ✓ (perfect)
└─ SM: 2.7 ✓ (good)
         ↓
Kiln Fired:
├─ Temperature: 1480°C (good)
├─ Dwell time: 25 min
└─ Cooling rate: 50°C/hr
         ↓
Clinker Produced:
├─ C3S: 65% ✓ HIGH (early strength expected)
├─ C2S: 18% ✓
├─ Free CaO: 1.2% ✓ (low, good quality)
└─ XRD confirmed phase composition
         ↓
Cement Ground:
├─ Fineness: 3600 cm²/g ✓ (high, fast hydration)
├─ Clinker: 95%
└─ Gypsum: 5%
         ↓
Concrete Tested:
├─ Mix: 450 kg/m³ cement
├─ W/C ratio: 0.45 ✓ (optimal)
├─ Curing: water for 28 days
└─ Result: 48.2 MPa ✓ EXCELLENT
```

**Explanation:** This cement has excellent strength because:
1. Raw mix LSF was perfect (1.00)
2. Kiln fired at ideal temperature (1480°C)
3. Clinker has high alite (65%) → high early strength
4. Cement is very fine (3600 cm²/g) → fast hydration
5. Concrete has low W/C (0.45) → dense matrix

---

## Integration with ML/Prediction Models

The lineage system provides features with **physical meaning**:

```python
# Features extracted from lineage
features = {
    # Raw material features
    "rm_cao_avg": 50.0,          # Average CaO in raw materials
    "rm_sio2_avg": 32.0,         # Average SiO2
    
    # Raw mix quality indices
    "raw_mix_lsf": 1.00,         # Lime saturation factor
    "raw_mix_sm": 2.7,           # Silica modulus
    
    # Kiln parameters
    "kiln_temp": 1480,           # Maximum temperature
    "kiln_dwell": 25,            # Dwell time
    
    # Clinker composition
    "clinker_c3s": 65.0,         # Alite content
    "clinker_free_cao": 1.2,     # Free lime
    
    # Cement properties
    "cement_fineness": 3600,     # Blaine fineness
    "cement_type": 0,            # OPC = 0, PPC = 1, etc.
    
    # Concrete mix
    "w_c_ratio": 0.45,           # Water-cement ratio
    "cement_content": 450,       # kg/m³
}

# Target: 28-day strength
target = 48.2  # MPa

# Model trains with meaningful features
# → Predictions are interpretable
# → Can explain "why this prediction"
```

---

## Next Steps

1. **Load your existing data** using `DataChainBuilder`
2. **Run the example** to verify the system works
3. **Train ML models** with full traceability
4. **Use explainer** to generate insights for each prediction
5. **Continuously add** new production batches and test results

---

## Support & Questions

Refer to:
- [LINEAGE_GUIDE.md](LINEAGE_GUIDE.md) - Detailed guide
- [example_lineage_demo.py](example_lineage_demo.py) - Working example
- Source code docstrings for API details

---

## Key Achievement

Now you can trace any cement strength back to its origin:

**"This cement has lower predicted 28-day strength because this raw-material combination produced lower alite (C3S=55% vs. 65%), which was associated with this lower kiln burnability, resulting in this clinker quality and this final cement behavior."**

Every prediction has a complete audit trail. 🎯
