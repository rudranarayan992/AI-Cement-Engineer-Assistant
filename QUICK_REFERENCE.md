# Quick Reference: Cement Data Lineage

## The Connected Chain

```
Raw_Materials (RM_001)
      ↓
Raw_Mix (RM_001) → LSF=1.00, SM=2.7, AM=2.5
      ↓
Kiln_Run (KR_001) → Temp=1480°C, Dwell=25 min
      ↓
Clinker (CK_001) → C3S=65%, C2S=18%, Free CaO=1.2%
      ↓
Cement (CB_001) → Fineness=3500 cm²/g, Type=OPC
      ↓
Strength_Test (ST_001) → 28-day=48.2 MPa, W/C=0.45
      ↓
Standards (STD_001) → Status=PASSED
```

## Key Quality Indices

| Index | Formula | Target | Too Low | Too High |
|-------|---------|--------|---------|----------|
| **LSF** | CaO/(2.8×SiO2+1.18×Al2O3+0.65×Fe2O3) | 0.95–1.05 | Weak cement | Durability issues |
| **SM** | SiO2/(Al2O3+Fe2O3) | 2.3–3.0 | Poor strength | Excess belite |
| **AM** | Al2O3/Fe2O3 | 2.0–3.0 | Too much ferrite | Excess aluminate |

## Phase Composition Impact

| Phase | % Range | Primary Role | Strength Target |
|-------|---------|--------------|-----------------|
| **C3S** (Alite) | 50–70% | Early strength (1–28 d) | **Higher C3S = Stronger cement** |
| **C2S** (Belite) | 15–30% | Late strength (28+ d) | Long-term durability |
| **C3A** (Aluminate) | 5–12% | Fast reaction | Setting time control |
| **C4AF** (Ferrite) | 5–15% | Color & minor contribution | Workability |
| **Free CaO** | <2.5% | Should be minimal | **Low = Better quality** |

## Strength Drivers

```
        28-day Strength (MPa)
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
Clinker Quality    Concrete Mix
    ↓                   ↓
  C3S %           ↙  ↓  ↖
  Free CaO        W/C Ratio
  Fineness        Curing
                  Time
```

### Simple Prediction
- **High C3S (65%) + Fine cement (3500) + Low W/C (0.45)** → ~48 MPa ✓
- **Low C3S (55%) + Coarse cement (2500) + High W/C (0.55)** → ~30 MPa ✗

## Critical Parameters

### Raw Mix Stage
- LSF between 0.95–1.05 → Good phase formation
- SM between 2.3–3.0 → Balanced strength
- Proportions documented for traceability

### Kiln Stage
- Temperature 1450–1500°C → Optimal clinkerization
- Dwell time 20–30 min → Sufficient reaction
- Cooling rate 40–60°C/hr → Phase stability

### Clinker Stage
- C3S 55–70% → Meets strength requirements
- Free CaO <2.5% → Quality indicator
- Fineness adequate → Grinding efficiency

### Cement Stage
- Fineness 2500–4000 cm²/g → Hydration rate
- Gypsum 3–5% → Setting time control
- Proper storage → Quality maintenance

### Concrete Stage
- W/C ratio 0.35–0.55 → Strength control
- Cement content 400–500 kg/m³ → Durability
- Proper curing → Strength development

## Code Quick Reference

### Create Data Chain
```python
from src.data_chain_loader import DataChainBuilder

builder = DataChainBuilder(db_path="cement.db")

# Stage 1: Raw Mix
raw_mix = builder.create_raw_mix_from_materials(
    raw_mix_id="RM_001",
    material_proportions={"RM_001": 70, "RM_002": 20, "RM_003": 10},
    materials={...}
)

# Stage 2: Kiln
kiln = builder.create_kiln_run(
    kiln_run_id="KR_001",
    raw_mix_id=raw_mix.raw_mix_id,
    maximum_temperature_celsius=1480
)

# Stage 3: Clinker
clinker = builder.create_clinker(
    clinker_id="CK_001",
    kiln_run_id=kiln.kiln_run_id,
    raw_mix_id=raw_mix.raw_mix_id,
    c3s_percent=65.0,
    free_cao_percent=1.2
)

# Stage 4: Cement
cement = builder.create_cement_batch(
    cement_batch_id="CB_001",
    clinker_id=clinker.clinker_id,
    kiln_run_id=kiln.kiln_run_id,
    raw_mix_id=raw_mix.raw_mix_id,
    fineness_cm2_g=3500
)

# Stage 5: Strength Test
test = builder.create_strength_test(
    strength_test_id="ST_001",
    cement_batch_id=cement.cement_batch_id,
    clinker_id=clinker.clinker_id,
    kiln_run_id=kiln.kiln_run_id,
    raw_mix_id=raw_mix.raw_mix_id,
    w_c_ratio=0.45,
    compressive_strength_28d_mpa=48.2
)
```

### Query Chain
```python
from src.data_integration import LineageDatabase

db = LineageDatabase("cement.db")
chain = db.get_lineage_chain("CB_001")

print(f"Materials: {[m['name'] for m in chain['raw_materials']]}")
print(f"LSF: {chain['raw_mix']['lsf']:.2f}")
print(f"Kiln Temp: {chain['kiln_run']['max_temp_celsius']}°C")
print(f"C3S: {chain['clinker']['c3s_percent']:.1f}%")
print(f"Fineness: {chain['cement']['fineness_cm2_g']} cm²/g")
print(f"Strength: {chain['strength_tests'][0]['strength_28d_mpa']:.1f} MPa")
```

### Explain Results
```python
from src.explainability.strength_explainer import StrengthExplainer
from src.data_lineage import LineageTrace

trace = LineageTrace()
# ... populate from database ...

explainer = StrengthExplainer(trace)
print(explainer.explain_strength_result(48.2))

# Get recommendations
for rec in explainer.get_recommendations():
    print(f"⚠ {rec}")
```

## Database Tables

```sql
-- Connection points (Foreign Keys)
raw_materials          ← Starting point
  ↓ (many-to-many)
raw_mix_composition    ← Links materials to mix
  ↓
raw_mixes              ← Quality indices here
  ↓
kiln_runs              ← References raw_mix_id
  ↓
clinkers               ← References kiln_run_id, raw_mix_id
  ↓
cement_batches         ← References clinker_id, kiln_run_id, raw_mix_id
  ↓
strength_tests         ← References cement_batch_id, clinker_id, etc.
  ↓
standards_compliance   ← References cement_batch_id, strength_test_id
```

## Typical Values

### Raw Mix (OPC)
- CaO: 62–66%
- SiO2: 19–23%
- Al2O3: 4–7%
- Fe2O3: 2–4%
- LSF: 0.95–1.05 ✓
- SM: 2.3–3.0 ✓
- AM: 2.0–3.0 ✓

### Clinker
- C3S: 50–70%
- C2S: 15–30%
- C3A: 5–12%
- C4AF: 5–15%
- Free CaO: <2.5%
- Fineness: 3000–3500 cm²/g

### Cement (OPC)
- Fineness: 2500–4000 cm²/g
- Clinker: 92–95%
- Gypsum: 3–5%
- Additives: 0–8%

### Concrete (28-day strength)
- W/C = 0.40 → 50–60 MPa
- W/C = 0.45 → 40–50 MPa
- W/C = 0.50 → 30–40 MPa
- W/C = 0.55 → 25–35 MPa
- W/C = 0.60 → 20–30 MPa

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Low early strength (7d) | Low C3S or coarse cement | Increase kiln temp or fineness |
| High free CaO | Underburnt clinker | Increase kiln temp or dwell |
| High LSF | Too much limestone | Reduce limestone in raw mix |
| Low LSF | Too much silica | Reduce silica or increase limestone |
| High w/c concrete | Poor workability | Reduce w/c, increase cement or add admixtures |
| False set in cement | High C3A | Control C3A%, add retarder |

## Standards Compliance

### OPC (33 Grade - IS 269:2015)
- 28-day strength: 33–43 MPa ✓
- Fineness: >2250 cm²/g
- LSF: 0.80–1.02
- Free CaO: <2.8%

### OPC (43 Grade - IS 8112:2013)
- 28-day strength: 43–53 MPa ✓
- Fineness: >3000 cm²/g
- Free CaO: <2.0%

## Reference Files

| File | Purpose |
|------|---------|
| `src/data_lineage.py` | Data models |
| `src/data_integration.py` | Database layer |
| `src/data_chain_loader.py` | Loading utilities |
| `src/explainability/strength_explainer.py` | Explanations |
| `example_lineage_demo.py` | Working example |
| `LINEAGE_GUIDE.md` | Detailed guide |
| `DATA_CHAIN_README.md` | Quick start |

## Run Example
```bash
python example_lineage_demo.py
```

Creates complete chain and shows:
- Raw materials ✓
- Raw mix with LSF/SM ✓
- Kiln run ✓
- Clinker phases ✓
- Cement batch ✓
- Strength test ✓
- Causal explanation ✓
- Recommendations ✓
