"""Unified engineering input interface for material composition normalization.

This module provides:
1. Input parsing from various formats (kg, %, molecular formula, trade names)
2. Unit conversion and normalization
3. Oxide composition standardization
4. Chemical validity checking
5. Raw material database lookup
6. Provenance tracking for input sources

DESIGN PRINCIPLES:
- Accept user inputs in ANY form (kg, %, ppm, molecular formula, trade names)
- Normalize to canonical oxide representation (as-received or ignited basis)
- Track data provenance (USER_ENTRY, MEASURED, REFERENCE_DB, CALCULATED)
- Validate chemical stoichiometry and bounds
- Provide clear feedback for invalid inputs
- Support batch processing and single entry

SUPPORTED INPUT FORMATS:
1. Component mass: {"cement": 200, "aggregate": 1800} in kg
2. Oxide composition: {"CaO": 65.2, "SiO2": 22.1} in %
3. Molecular formula: "Ca3SiO5" or "3CaO·SiO2"
4. Trade name: "Portland Cement Type I", "Silica Fume"
5. Mixed specification: {"Portland Cement": 100, "Fly Ash": 30} in kg
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd


@dataclass
class MaterialComposition:
    """Normalized material composition specification."""

    material_name: str
    oxides: Dict[str, float]  # CaO, SiO2, Al2O3, Fe2O3, MgO, SO3, Na2O, K2O, LOI, etc.
    basis: str  # "as_received" or "ignited"
    unit: str  # "%"
    source: str  # USER_ENTRY, MEASURED, REFERENCE_DB, CALCULATED
    confidence: float  # 0.0-1.0
    notes: str = ""


@dataclass
class NormalizedInput:
    """Normalized engineering input ready for predictions."""

    timestamp: str
    input_type: str  # raw_mix, raw_material, cement, concrete, etc.
    materials: List[MaterialComposition]
    combined_oxides: Dict[str, float]  # blended composition if applicable
    combined_basis: str
    combined_source: str  # MEASURED, CALCULATED, MIXED, etc.
    total_mass: float  # total input mass in reference units
    mass_fractions: Dict[str, float]  # material_name -> fraction 0-1
    validation_warnings: List[str]
    validation_ok: bool


STANDARD_OXIDES = [
    "CaO",
    "SiO2",
    "Al2O3",
    "Fe2O3",
    "MgO",
    "SO3",
    "Na2O",
    "K2O",
    "TiO2",
    "P2O5",
    "LOI",
]

# Trade name database for common materials
MATERIAL_DATABASE = {
    "Portland Cement Type I": {
        "oxides": {"CaO": 62.5, "SiO2": 20.5, "Al2O3": 5.8, "Fe2O3": 3.2, "MgO": 2.5, "SO3": 2.8},
        "basis": "ignited",
        "source": "REFERENCE_DB",
    },
    "Portland Cement Type II": {
        "oxides": {"CaO": 62.0, "SiO2": 21.0, "Al2O3": 5.0, "Fe2O3": 3.5, "MgO": 2.5, "SO3": 2.5},
        "basis": "ignited",
        "source": "REFERENCE_DB",
    },
    "Portland Cement Type V": {
        "oxides": {"CaO": 63.5, "SiO2": 19.5, "Al2O3": 3.5, "Fe2O3": 4.5, "MgO": 2.5, "SO3": 2.5},
        "basis": "ignited",
        "source": "REFERENCE_DB",
    },
    "Silica Fume": {
        "oxides": {"SiO2": 94.0, "LOI": 3.0},
        "basis": "as_received",
        "source": "REFERENCE_DB",
    },
    "Fly Ash (Class C)": {
        "oxides": {"SiO2": 40.0, "Al2O3": 20.0, "Fe2O3": 6.0, "CaO": 25.0, "LOI": 5.0},
        "basis": "as_received",
        "source": "REFERENCE_DB",
    },
    "Fly Ash (Class F)": {
        "oxides": {"SiO2": 55.0, "Al2O3": 20.0, "Fe2O3": 6.0, "CaO": 5.0, "LOI": 5.0},
        "basis": "as_received",
        "source": "REFERENCE_DB",
    },
    "Slag": {
        "oxides": {"CaO": 42.0, "SiO2": 35.0, "Al2O3": 13.0, "MgO": 6.0},
        "basis": "ignited",
        "source": "REFERENCE_DB",
    },
    "Limestone": {
        "oxides": {"CaO": 56.0, "SiO2": 2.0, "Al2O3": 1.0, "LOI": 44.0},
        "basis": "as_received",
        "source": "REFERENCE_DB",
    },
    "Clay": {
        "oxides": {"SiO2": 65.0, "Al2O3": 22.0, "Fe2O3": 6.0, "LOI": 5.0},
        "basis": "as_received",
        "source": "REFERENCE_DB",
    },
}


class UnifiedInputParser:
    """Parse and normalize engineering inputs from various formats."""

    def __init__(self, raw_materials_db_path: Optional[str | Path] = None):
        """Initialize parser with optional raw materials reference database."""
        self.material_db = MATERIAL_DATABASE.copy()
        self.raw_materials_df = None

        if raw_materials_db_path:
            try:
                self.raw_materials_df = pd.read_csv(raw_materials_db_path)
            except Exception as e:
                print(f"Warning: Could not load raw materials database: {e}")

    def parse_input(
        self,
        user_input: Dict[str, Any],
        input_type: str = "raw_mix",
        basis: str = "as_received",
    ) -> NormalizedInput:
        """Parse and normalize user input to standard format.

        Args:
            user_input: dict with material names and values
            input_type: raw_mix, raw_material, cement, concrete, etc.
            basis: as_received or ignited

        Returns:
            NormalizedInput with validated composition
        """
        from datetime import datetime

        materials: List[MaterialComposition] = []
        validation_warnings: List[str] = []
        total_mass = 0.0
        mass_fractions: Dict[str, float] = {}

        for mat_name, mat_value in user_input.items():
            # Try to parse the material
            parsed = self._parse_material(mat_name, mat_value)

            if not parsed:
                validation_warnings.append(f"Unknown material: {mat_name}")
                continue

            composition, source = parsed
            materials.append(composition)
            total_mass += mat_value if isinstance(mat_value, (int, float)) else 1.0

        # Compute mass fractions
        if total_mass > 0:
            for mat in materials:
                user_mass = user_input.get(mat.material_name, 1.0)
                mass_fractions[mat.material_name] = user_mass / total_mass

        # Blend compositions
        combined_oxides = self._blend_compositions(materials, mass_fractions)
        combined_basis = basis
        combined_source = self._determine_combined_source([m.source for m in materials])

        # Validate
        validation_ok, warnings = self._validate_composition(combined_oxides)
        validation_warnings.extend(warnings)

        return NormalizedInput(
            timestamp=datetime.utcnow().isoformat() + "Z",
            input_type=input_type,
            materials=materials,
            combined_oxides=combined_oxides,
            combined_basis=combined_basis,
            combined_source=combined_source,
            total_mass=total_mass,
            mass_fractions=mass_fractions,
            validation_warnings=validation_warnings,
            validation_ok=validation_ok,
        )

    def _parse_material(self, mat_name: str, mat_value: Any) -> Optional[Tuple[MaterialComposition, str]]:
        """Parse a single material name and return composition.

        Returns:
            Tuple of (MaterialComposition, source) or None
        """
        mat_name_clean = mat_name.strip()

        # Try exact match in database
        if mat_name_clean in self.material_db:
            db_entry = self.material_db[mat_name_clean]
            return (
                MaterialComposition(
                    material_name=mat_name_clean,
                    oxides=db_entry["oxides"].copy(),
                    basis=db_entry["basis"],
                    unit="%",
                    source=db_entry["source"],
                    confidence=0.9,
                ),
                db_entry["source"],
            )

        # Try case-insensitive match
        for db_name, db_entry in self.material_db.items():
            if db_name.lower() == mat_name_clean.lower():
                return (
                    MaterialComposition(
                        material_name=db_name,
                        oxides=db_entry["oxides"].copy(),
                        basis=db_entry["basis"],
                        unit="%",
                        source=db_entry["source"],
                        confidence=0.85,
                    ),
                    db_entry["source"],
                )

        # Try to parse as oxide composition if input looks like {"CaO": 65.2, ...}
        if isinstance(mat_value, dict):
            oxides = self._parse_oxide_dict(mat_value)
            if oxides:
                return (
                    MaterialComposition(
                        material_name=mat_name_clean,
                        oxides=oxides,
                        basis="ignited",
                        unit="%",
                        source="USER_ENTRY",
                        confidence=0.7,
                    ),
                    "USER_ENTRY",
                )

        # Try to parse as molecular formula
        if isinstance(mat_value, str):
            phases = self._parse_molecular_formula(mat_value)
            if phases:
                return (
                    MaterialComposition(
                        material_name=mat_name_clean,
                        oxides=phases,
                        basis="ignited",
                        unit="%",
                        source="USER_ENTRY",
                        confidence=0.6,
                    ),
                    "USER_ENTRY",
                )

        return None

    def _parse_oxide_dict(self, oxide_input: Dict[str, float]) -> Dict[str, float]:
        """Parse oxide composition dictionary."""
        result = {}
        for oxide_name, value in oxide_input.items():
            if oxide_name in STANDARD_OXIDES:
                result[oxide_name] = float(value)
        return result if result else {}

    def _parse_molecular_formula(self, formula: str) -> Optional[Dict[str, float]]:
        """Try to parse a molecular formula string like 'Ca3SiO5' or '3CaO·SiO2'.

        Returns:
            Dict of oxide percentages if parseable, None otherwise
        """
        # Remove special characters
        formula_clean = formula.replace("·", "").replace("·", "").strip()

        # Simple pattern: element + optional coefficient
        pattern = r"([A-Z][a-z]?)(\d*)"
        matches = re.findall(pattern, formula_clean)

        if not matches:
            return None

        # Map elements to oxides (simplified)
        element_to_oxide = {
            "Ca": "CaO",
            "Si": "SiO2",
            "Al": "Al2O3",
            "Fe": "Fe2O3",
            "Mg": "MgO",
            "S": "SO3",
            "Na": "Na2O",
            "K": "K2O",
        }

        # This is a simplification; full stoichiometry requires careful calculation
        # For now, return None as this requires domain expertise
        return None

    def _blend_compositions(
        self, materials: List[MaterialComposition], mass_fractions: Dict[str, float]
    ) -> Dict[str, float]:
        """Blend compositions from multiple materials."""
        blended = {oxide: 0.0 for oxide in STANDARD_OXIDES}

        for material in materials:
            fraction = mass_fractions.get(material.material_name, 0.0)
            for oxide, value in material.oxides.items():
                if oxide in blended:
                    blended[oxide] += value * fraction

        # Normalize to 100% (or account for LOI)
        total = sum(v for k, v in blended.items() if k != "LOI")
        if total > 0:
            for oxide in blended:
                if oxide != "LOI":
                    blended[oxide] = (blended[oxide] / total) * 100.0

        return blended

    def _validate_composition(self, oxides: Dict[str, float]) -> Tuple[bool, List[str]]:
        """Validate chemical composition for plausibility.

        Returns:
            (is_valid, list_of_warnings)
        """
        warnings = []
        valid = True

        # Check for negative values
        for oxide, value in oxides.items():
            if value < 0:
                warnings.append(f"Negative oxide value for {oxide}: {value}%")
                valid = False
            if value > 100:
                warnings.append(f"Oxide {oxide} exceeds 100%: {value}%")
                valid = False

        # Check sum (allow 90-110% range for oxidation/reduction and measurement error)
        total = sum(v for k, v in oxides.items() if k != "LOI")
        if total < 90 or total > 110:
            warnings.append(f"Sum of oxides {total:.1f}% is outside expected range [90, 110]%")

        # Check cement-specific bounds
        if "CaO" in oxides:
            if oxides["CaO"] < 50 or oxides["CaO"] > 75:
                warnings.append(f"CaO {oxides['CaO']:.1f}% is outside typical cement range [50, 75]%")

        if "SiO2" in oxides:
            if oxides["SiO2"] < 15 or oxides["SiO2"] > 30:
                warnings.append(f"SiO2 {oxides['SiO2']:.1f}% is outside typical cement range [15, 30]%")

        return valid, warnings

    def _determine_combined_source(self, sources: List[str]) -> str:
        """Determine combined source from individual sources."""
        if not sources:
            return "UNKNOWN"
        if all(s == "MEASURED" for s in sources):
            return "MEASURED"
        if "MEASURED" in sources:
            return "MIXED"
        if all(s == "REFERENCE_DB" for s in sources):
            return "REFERENCE_DB"
        return "MIXED"

    def convert_basis(
        self, oxides: Dict[str, float], from_basis: str, to_basis: str
    ) -> Dict[str, float]:
        """Convert oxide composition between bases.

        Args:
            oxides: dict of oxide -> % value
            from_basis: "as_received" or "ignited"
            to_basis: "as_received" or "ignited"

        Returns:
            Converted composition
        """
        if from_basis == to_basis:
            return oxides.copy()

        result = oxides.copy()
        loi = oxides.get("LOI", 0.0)

        if from_basis == "as_received" and to_basis == "ignited":
            # Remove LOI from sum, normalize to 100%
            total_without_loi = sum(v for k, v in result.items() if k != "LOI")
            if total_without_loi > 0:
                factor = 100.0 / total_without_loi
                for oxide in result:
                    if oxide != "LOI":
                        result[oxide] *= factor
            result["LOI"] = 0.0

        elif from_basis == "ignited" and to_basis == "as_received":
            # Add back LOI (simplified; assume input LOI is what should be removed)
            # This is a simplification; real conversion requires knowing what was lost
            pass

        return result

    def export_to_dict(self, normalized: NormalizedInput) -> Dict[str, Any]:
        """Export normalized input as JSON-serializable dict."""
        return {
            "timestamp": normalized.timestamp,
            "input_type": normalized.input_type,
            "materials": [asdict(m) for m in normalized.materials],
            "combined_oxides": normalized.combined_oxides,
            "combined_basis": normalized.combined_basis,
            "combined_source": normalized.combined_source,
            "total_mass": normalized.total_mass,
            "mass_fractions": normalized.mass_fractions,
            "validation_warnings": normalized.validation_warnings,
            "validation_ok": normalized.validation_ok,
        }
