"""Chemistry feature engineering for cement process.

This module transforms raw cement/clinker chemistry data into derived features
using established cement chemistry formulas and the physics validation layer.

DESIGN PRINCIPLES:

1. No silent data substitution: If a required oxide is missing, the feature is NaN.
2. Explicit basis tracking: All calculations specify their basis assumption.
3. Leakage-safe feature engineering: Features depend only on legitimate inputs.
4. Provenance tracking: Every feature records its source, formula, and calculation details.
5. Validation integration: Uses existing physics_constraints for plausibility checks.
6. Bogue as reference: Bogue phases are labeled as reference/benchmark, not measured data.

SCIENTIFIC CONTEXT:

This module implements cement chemistry calculations based on:
- Lea's Chemistry of Cement and Concrete
- Bogue's empirical phase estimation (1955)
- Standard clinker composition analysis

Calculations assume:
- Oxide compositions on ignited basis (LOI removed) where specified
- End-member phase stoichiometry (idealized; real clinker deviates ~5-10%)
- Bogue formulas are empirical estimates, NOT exact laboratory measurements

REFERENCE DATASETS:

This module is designed to work with cement process data organized as:

1. Raw Materials (raw_materials_database.csv):
   - Sample_ID, Material_Type, oxide percentages (as-received), LOI

2. Raw Meal Samples (raw_meal_samples.csv):
   - Batch_ID, Raw_CaO, Raw_SiO2, ..., Raw_MgO, Raw_SO3, LOI
   - Basis: as-received (before kiln burning)
   - Units: weight percent

3. Clinker Analysis (clinker_analysis.csv):
   - Batch_ID, Clinker_CaO, Clinker_SiO2, ..., LSF, SM, AM, Free_CaO_pct
   - Basis: ignited (LOI-removed)
   - Includes pre-computed moduli and Bogue phases for comparison
   - Units: weight percent

4. Cement Quality (cement_quality.csv):
   - Batch_ID, Blaine, Gypsum_SO3_pct, WC_Ratio, Strength (3d/7d/28d)
   - Post-clinker cement properties

Join key: Batch_ID (links raw_meal → clinker → cement)

NO DATA MERGE: This module does NOT combine concrete benchmark with cement data.

"""

from __future__ import annotations

import math
import sys
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

# Relative imports from sibling packages
from ..chemistry import chemistry_engine as _ce
from ..chemistry import raw_mix as _raw_mix
from ..validation import physics_constraints as _pc


@dataclass
class FeatureProvenance:
    """Metadata tracking the lineage and safety of a computed feature.
    
    Every feature must have complete provenance to enable:
    - Leakage auditing
    - Basis verification
    - Source validation
    - Formula documentation
    """

    feature_name: str
    """Name of the computed feature (e.g., 'LSF', 'bogue_reference_C3S')."""

    source_variables: List[str]
    """List of input variable names required to compute this feature."""

    formula: str
    """Mathematical formula or reference (e.g., 'CaO / (2.8*SiO2 + 1.18*Al2O3 + 0.65*Fe2O3)')."""

    basis: str
    """Chemistry basis assumption ('as_received', 'dry', 'ignited')."""

    units: str
    """Units of the computed feature (e.g., 'percent', 'dimensionless')."""

    calculation_method: str
    """Brief description ('measured' if from raw data, 'computed' if derived, 'reference' if Bogue)."""

    target_derived: bool = False
    """True if this feature is mathematically derived from the model target variable."""

    leakage_risk: str = "SAFE"
    """Leakage classification: 'SAFE', 'CONDITIONAL', 'LEAKAGE_RISK'."""

    leakage_notes: str = ""
    """Detailed explanation of leakage risk and mitigation strategy if applicable."""

    source_dataset: str = ""
    """Dataset file name or module where data originates (e.g., 'raw_meal_samples.csv')."""

    timestamp_if_available: bool = False
    """Whether this feature is associated with a timestamp (for temporal validation)."""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize provenance to dictionary."""
        return {
            "feature_name": self.feature_name,
            "source_variables": self.source_variables,
            "formula": self.formula,
            "basis": self.basis,
            "units": self.units,
            "calculation_method": self.calculation_method,
            "target_derived": self.target_derived,
            "leakage_risk": self.leakage_risk,
            "leakage_notes": self.leakage_notes,
            "source_dataset": self.source_dataset,
            "timestamp_if_available": self.timestamp_if_available,
        }


@dataclass
class ChemistryFeatureSet:
    """Complete feature set with provenance tracking and validation results.
    
    This dataclass holds:
    - Computed features (LSF, SM, AM, Bogue phases)
    - Provenance for each feature
    - Validation results
    - Warnings and data quality flags
    """

    batch_id: str
    """Identifier for this batch (e.g., 'BATCH_0001')."""

    input_oxides: Dict[str, float]
    """Input oxide composition (as-received or ignited basis as specified)."""

    input_basis: str
    """Basis of input oxides ('as_received', 'dry', 'ignited')."""

    lsf: Optional[float] = None
    """Lime Saturation Factor (dimensionless)."""

    sm: Optional[float] = None
    """Silica Modulus (dimensionless)."""

    am: Optional[float] = None
    """Alumina Modulus (dimensionless)."""

    bogue_reference_c3s: Optional[float] = None
    """Bogue empirical C3S estimate (reference/benchmark, mass %)."""

    bogue_reference_c2s: Optional[float] = None
    """Bogue empirical C2S estimate (reference/benchmark, mass %)."""

    bogue_reference_c3a: Optional[float] = None
    """Bogue empirical C3A estimate (reference/benchmark, mass %)."""

    bogue_reference_c4af: Optional[float] = None
    """Bogue empirical C4AF estimate (reference/benchmark, mass %)."""

    feature_provenances: Dict[str, FeatureProvenance] = field(default_factory=dict)
    """Provenance metadata for each computed feature."""

    validation_results: Dict[str, Any] = field(default_factory=dict)
    """Results from physics_constraints validation layer."""

    warnings: List[str] = field(default_factory=list)
    """Non-fatal warnings about data quality or computation."""

    computation_valid: bool = True
    """True if all computations were numerically sound."""

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to single-row DataFrame for integration with ML pipelines.
        
        Returns DataFrame with columns:
        - batch_id
        - lsf, sm, am
        - bogue_reference_c3s, bogue_reference_c2s, bogue_reference_c3a, bogue_reference_c4af
        
        NaN values indicate missing/invalid computations.
        """
        return pd.DataFrame(
            [
                {
                    "batch_id": self.batch_id,
                    "lsf": self.lsf,
                    "sm": self.sm,
                    "am": self.am,
                    "bogue_reference_c3s": self.bogue_reference_c3s,
                    "bogue_reference_c2s": self.bogue_reference_c2s,
                    "bogue_reference_c3a": self.bogue_reference_c3a,
                    "bogue_reference_c4af": self.bogue_reference_c4af,
                }
            ]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary including provenance and validation."""
        return {
            "batch_id": self.batch_id,
            "input_oxides": self.input_oxides,
            "input_basis": self.input_basis,
            "features": {
                "lsf": self.lsf,
                "sm": self.sm,
                "am": self.am,
                "bogue_reference_c3s": self.bogue_reference_c3s,
                "bogue_reference_c2s": self.bogue_reference_c2s,
                "bogue_reference_c3a": self.bogue_reference_c3a,
                "bogue_reference_c4af": self.bogue_reference_c4af,
            },
            "provenances": {k: v.to_dict() for k, v in self.feature_provenances.items()},
            "validation": self.validation_results,
            "warnings": self.warnings,
            "computation_valid": self.computation_valid,
        }


def extract_cement_chemistry_features(
    oxide_data: Dict[str, float],
    batch_id: str = "unknown",
    input_basis: str = "as_received",
    free_cao: Optional[float] = None,
    so3: Optional[float] = None,
) -> ChemistryFeatureSet:
    """Extract derived cement chemistry features from raw oxide composition.

    This function computes chemistry-derived features (LSF, SM, AM, Bogue phases)
    from oxide composition, with explicit basis handling, provenance tracking,
    and physics validation.

    Args:
        oxide_data: Dictionary mapping oxide names to values (percent).
                   Expected keys: 'CaO', 'SiO2', 'Al2O3', 'Fe2O3', 'MgO', 'SO3'.
                   Values are numeric; None or NaN treated as missing.
        batch_id: Identifier for this batch (for tracking).
        input_basis: Basis of input oxides ('as_received', 'dry', 'ignited').
                    LSF/SM/AM calculations assume ignited basis.
        free_cao: Free CaO percentage (optional, required for Bogue calculation).
                 If None, Bogue calculation is skipped with warning.
        so3: SO3 percentage (optional, required for Bogue calculation).
             If None, defaults to oxide_data.get('SO3', 0.0).

    Returns:
        ChemistryFeatureSet containing computed features, provenance, validation results.

    Raises:
        ValueError: If oxide_data is None or empty.
        TypeError: If oxide_data is not a mapping.

    Notes:
        - No silent zero substitution: Missing oxides → NaN features
        - Bogue phases labeled as 'reference' (empirical, not measured)
        - All calculations use existing chemistry_engine functions
        - Results validated against physics_constraints limits
    """
    if not oxide_data:
        raise ValueError("oxide_data cannot be empty")
    if not isinstance(oxide_data, dict):
        raise TypeError(f"oxide_data must be a dict, got {type(oxide_data)}")

    # Initialize result object
    result = ChemistryFeatureSet(
        batch_id=batch_id,
        input_oxides=dict(oxide_data),
        input_basis=input_basis,
    )

    warnings: List[str] = []

    # Extract key oxides
    cao = oxide_data.get("CaO")
    sio2 = oxide_data.get("SiO2")
    al2o3 = oxide_data.get("Al2O3")
    fe2o3 = oxide_data.get("Fe2O3")

    # Validate numeric types
    for name, val in [("CaO", cao), ("SiO2", sio2), ("Al2O3", al2o3), ("Fe2O3", fe2o3)]:
        if val is not None:
            try:
                float(val)
            except (TypeError, ValueError):
                warnings.append(f"Oxide '{name}' is non-numeric: {val}")
                return result  # Cannot proceed with invalid chemistry

    # Check for missing oxides
    missing = [name for name, val in [("CaO", cao), ("SiO2", sio2), ("Al2O3", al2o3), ("Fe2O3", fe2o3)] if val is None or (isinstance(val, float) and math.isnan(val))]
    if missing:
        warnings.append(f"Missing required oxides: {missing}. Features will be NaN.")
        result.lsf = float("nan")
        result.sm = float("nan")
        result.am = float("nan")
        result.warnings = warnings
        result.computation_valid = False
        return result

    # Convert to float
    cao_f = float(cao)
    sio2_f = float(sio2)
    al2o3_f = float(al2o3)
    fe2o3_f = float(fe2o3)

    # Handle basis: if input is not ignited and LOI provided, convert to ignited basis
    used_oxides = {
        "CaO": cao_f,
        "SiO2": sio2_f,
        "Al2O3": al2o3_f,
        "Fe2O3": fe2o3_f,
    }
    if input_basis != "ignited":
        if "LOI" in oxide_data and oxide_data.get("LOI") is not None and not (isinstance(oxide_data.get("LOI"), float) and math.isnan(oxide_data.get("LOI"))):
            try:
                ign, mult = _raw_mix.ignited_basis(oxide_data)
                used_oxides = {
                    "CaO": float(ign.get("CaO")),
                    "SiO2": float(ign.get("SiO2")),
                    "Al2O3": float(ign.get("Al2O3")),
                    "Fe2O3": float(ign.get("Fe2O3")),
                }
                warnings.append(f"Input basis '{input_basis}' converted to ignited basis using LOI multiplier {mult:.4f}.")
            except Exception as e:
                warnings.append(f"Failed to convert to ignited basis: {e}")
                result.warnings = warnings
                result.computation_valid = False
                return result
        else:
            warnings.append(
                "Input basis is not 'ignited' and LOI not provided; assuming provided oxide values are ignited-basis for computation."
            )

    # Check for physically impossible values
    numeric_issue = False
    for name, val in [("CaO", cao_f), ("SiO2", sio2_f), ("Al2O3", al2o3_f), ("Fe2O3", fe2o3_f)]:
        if math.isnan(val) or math.isinf(val):
            warnings.append(f"Oxide '{name}' has invalid value: {val}")
            result.lsf = float("nan")
            result.sm = float("nan")
            result.am = float("nan")
            result.warnings = warnings
            result.computation_valid = False
            return result
        if val < 0:
            warnings.append(f"Oxide '{name}' is negative: {val} (physically impossible)")
            numeric_issue = True

    # --- LSF Calculation ---
    try:
        lsf = _ce.calculate_lsf(used_oxides["CaO"], used_oxides["SiO2"], used_oxides["Al2O3"], used_oxides["Fe2O3"], basis="ignited")
        # chemistry_engine returns percent-scale LSF for ignited-basis; convert to dimensionless fraction consistent with tests
        # If LSF returned as percent (e.g., 92.0), scale to 0.92 for downstream usage
        try:
            lsf_val = float(lsf)
            if lsf_val > 2.0:  # heuristic: if >2 assume percent-scale
                lsf_val = lsf_val / 100.0
        except Exception:
            lsf_val = float(lsf)
        result.lsf = float(lsf_val)
        result.feature_provenances["lsf"] = FeatureProvenance(
            feature_name="lsf",
            source_variables=["CaO", "SiO2", "Al2O3", "Fe2O3"],
            formula="CaO / (2.8*SiO2 + 1.18*Al2O3 + 0.65*Fe2O3)",
            basis=input_basis,
            units="dimensionless (percent scale)",
            calculation_method="computed",
            target_derived=False,
            leakage_risk="SAFE",
            leakage_notes="Computed directly from oxide composition, not target-derived.",
            source_dataset="raw_meal_samples.csv or clinker_analysis.csv",
        )
    except Exception as e:
        result.lsf = float("nan")
        warnings.append(f"LSF calculation failed: {e}")

    # --- SM Calculation ---
    try:
        sm = _ce.calculate_sm(used_oxides["SiO2"], used_oxides["Al2O3"], used_oxides["Fe2O3"], basis="ignited")
        result.sm = float(sm)
        result.feature_provenances["sm"] = FeatureProvenance(
            feature_name="sm",
            source_variables=["SiO2", "Al2O3", "Fe2O3"],
            formula="SiO2 / (Al2O3 + Fe2O3)",
            basis=input_basis,
            units="dimensionless",
            calculation_method="computed",
            target_derived=False,
            leakage_risk="SAFE",
            leakage_notes="Computed directly from oxide composition, not target-derived.",
            source_dataset="raw_meal_samples.csv or clinker_analysis.csv",
        )
    except Exception as e:
        result.sm = float("nan")
        warnings.append(f"SM calculation failed: {e}")

    # --- AM Calculation ---
    try:
        am = _ce.calculate_am(used_oxides["Al2O3"], used_oxides["Fe2O3"], basis="ignited")
        result.am = float(am)
        result.feature_provenances["am"] = FeatureProvenance(
            feature_name="am",
            source_variables=["Al2O3", "Fe2O3"],
            formula="Al2O3 / Fe2O3",
            basis=input_basis,
            units="dimensionless",
            calculation_method="computed",
            target_derived=False,
            leakage_risk="SAFE",
            leakage_notes="Computed directly from oxide composition, not target-derived.",
            source_dataset="raw_meal_samples.csv or clinker_analysis.csv",
        )
    except Exception as e:
        result.am = float("nan")
        warnings.append(f"AM calculation failed: {e}")

    # --- Bogue Phase Calculation (Reference) ---
    if free_cao is not None and not (isinstance(free_cao, float) and math.isnan(free_cao)):
        so3_val = so3 if so3 is not None else oxide_data.get("SO3", 0.0)
        try:
            from src.chemistry import clinker_chemistry as _clinker
        except Exception:
            try:
                from ..chemistry import clinker_chemistry as _clinker
            except Exception:
                import importlib.util
                import os
                clinker_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "chemistry",
                    "clinker_chemistry.py"
                )
                spec = importlib.util.spec_from_file_location("clinker_chemistry", clinker_path)
                _clinker = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(_clinker)

        try:
            bogue_oxide_data = {
                "CaO": cao_f,
                "SiO2": sio2_f,
                "Al2O3": al2o3_f,
                "Fe2O3": fe2o3_f,
                "SO3": float(so3_val) if so3_val is not None else 0.0,
                "Free_CaO": float(free_cao),
            }
            bogue_phases = _clinker.calculate_bogue_phases(bogue_oxide_data)

            result.bogue_reference_c3s = bogue_phases.get("C3S")
            result.bogue_reference_c2s = bogue_phases.get("C2S")
            result.bogue_reference_c3a = bogue_phases.get("C3A")
            result.bogue_reference_c4af = bogue_phases.get("C4AF")

            for phase_name in ["C3S", "C2S", "C3A", "C4AF"]:
                result.feature_provenances[f"bogue_reference_{phase_name.lower()}"] = FeatureProvenance(
                    feature_name=f"bogue_reference_{phase_name.lower()}",
                    source_variables=["CaO", "SiO2", "Al2O3", "Fe2O3", "SO3", "Free_CaO"],
                    formula=f"Bogue empirical {phase_name} calculation (Bogue 1955)",
                    basis=input_basis,
                    units="mass percent",
                    calculation_method="reference",
                    target_derived=False,
                    leakage_risk="CONDITIONAL",
                    leakage_notes=(
                        "Bogue phases are empirical estimates based on oxide composition. "
                        "These should not be treated as measured XRD phase labels. "
                        "Use as reference/benchmark only. Real clinker deviates 5-10% from Bogue estimates."
                    ),
                    source_dataset="clinker_analysis.csv (Free_CaO) + raw_meal_samples.csv (oxides)",
                )
        except Exception as e:
            warnings.append(f"Bogue phase calculation failed: {e}")
    else:
        warnings.append(
            "Free CaO not provided. Bogue phase calculations skipped. "
            "Provide free_cao parameter to enable Bogue feature calculation."
        )

    # --- Physics Validation ---
    try:
        validation = _pc.validate_chemistry_values(oxide_data)
        validation.update(
            _pc.validate_moduli(cao_f, sio2_f, al2o3_f, fe2o3_f)
        )
        result.validation_results = validation
        if not validation.get("valid", False):
            for violation in validation.get("violations", []):
                warnings.append(f"Validation violation: {violation}")
    except Exception as e:
        warnings.append(f"Physics validation failed: {e}")

    result.warnings = warnings
    # If any numeric_issue flagged (negative oxide values), mark computation invalid
    try:
        numeric_flag = numeric_issue  # defined above when checking numeric values
    except NameError:
        numeric_flag = False

    if numeric_flag:
        result.computation_valid = False
    else:
        # Mark invalid if any failure/invalid keywords present in warnings
        joined = " ".join(warnings).lower()
        result.computation_valid = not any(k in joined for k in ("failed", "invalid"))

    return result


def extract_multiple_chemistry_features(
    oxide_dataframe: pd.DataFrame,
    batch_id_column: str = "Batch_ID",
    basis: str = "as_received",
    cao_column: str = "CaO",
    sio2_column: str = "SiO2",
    al2o3_column: str = "Al2O3",
    fe2o3_column: str = "Fe2O3",
    free_cao_column: Optional[str] = None,
    so3_column: Optional[str] = None,
) -> pd.DataFrame:
    """Batch extract chemistry features from a DataFrame of multiple samples.

    Args:
        oxide_dataframe: DataFrame with oxide columns and batch_id.
        batch_id_column: Name of batch ID column.
        basis: Basis assumption for all rows ('as_received', 'dry', 'ignited').
        cao_column, sio2_column, al2o3_column, fe2o3_column: Oxide column names.
        free_cao_column: Name of Free CaO column (optional).
        so3_column: Name of SO3 column (optional).

    Returns:
        DataFrame with computed features (lsf, sm, am, bogue_reference_*).
        Rows with missing/invalid chemistry have NaN features.
    """
    results = []

    for idx, row in oxide_dataframe.iterrows():
        batch_id = str(row.get(batch_id_column, f"row_{idx}"))

        oxide_dict = {
            "CaO": row.get(cao_column),
            "SiO2": row.get(sio2_column),
            "Al2O3": row.get(al2o3_column),
            "Fe2O3": row.get(fe2o3_column),
        }

        # Handle optional inputs
        if so3_column and so3_column in row.index:
            oxide_dict["SO3"] = row.get(so3_column)

        free_cao = row.get(free_cao_column) if free_cao_column else None
        so3 = row.get(so3_column) if so3_column else None

        feature_set = extract_cement_chemistry_features(
            oxide_dict,
            batch_id=batch_id,
            input_basis=basis,
            free_cao=free_cao,
            so3=so3,
        )

        results.append(feature_set.to_dataframe())

    return pd.concat(results, ignore_index=True) if results else pd.DataFrame()
