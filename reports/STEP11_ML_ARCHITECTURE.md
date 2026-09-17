# STEP 11 — Real Cement/Clinker ML Architecture

## Status

CURRENTLY IMPLEMENTED:
- The repository already contains chemistry, validation, preprocessing, uncertainty, and training interfaces for the separate concrete benchmark and the deterministic cement process analytics pipeline.
- These modules are retained as the engineering foundation for future industrial ML.

FUTURE INTERFACE:
- The new architecture defines safe, reusable interfaces for real cement/clinker model development without training a model yet.
- All future model logic is organized as contracts, schemas, and validation interfaces that accept measured industrial data later.

REQUIRES REAL INDUSTRIAL DATA:
- Any actual cement/clinker prediction model must be trained on measured plant/lab ground truth.
- Synthetic labels, Bogue-derived values, and demo tables are explicitly excluded from future training targets.

## Architecture Summary

The design preserves five scientific boundaries:
1. Concrete benchmark remains separate from cement/clinker datasets.
2. Measured experimental targets are required for training.
3. Bogue values remain reference-only, not XRD/Rietveld ground truth.
4. Online features are distinct from post-production diagnostic features.
5. Physics/chemistry validation remains separate from ordinary ML prediction.

## Implemented Components

- Chemistry utilities: existing `src/chemistry/*` modules
- Physics validation: existing `src/validation/physics_constraints.py`
- OOD and uncertainty: existing `src/uncertainty/ood.py`
- Preprocessing: existing `src/preprocessing/data_preprocessing.py`
- Baseline models: existing `src/training/baseline_models.py` (concrete baseline only)
- Feature layer: existing `src/features/chemistry_features.py`
- Process pipeline: `src/pipeline/cement_process_pipeline.py`
- New future ML interface: `src/future_ml/cement_ml_architecture.py`

## Future ML Interface Layers

- Target taxonomy and measurement policy
- Feature policy (online vs post-production)
- Data contracts for raw materials, raw mix, kiln feed, process, clinker, and cement measurements
- Temporal alignment interface with explicit residence time configuration
- Chronological validation strategy
- Model configuration interface for Ridge, Random Forest, SVR, XGBoost, neural network, and Gaussian process
- Physics/chemistry validation layer separated from the ML model
- Stoichiometric reconstruction hook for future validation only
- OOD and uncertainty interfaces
- XAI metadata interface
- Optimization interface (design only)
- LLM deterministic-tool interface
- Model metadata tracking schema

## Implementation Status

This step implements the architecture and data contracts only. It does not train a real cement/clinker model, does not generate fake labels, and does not claim predictive accuracy.
