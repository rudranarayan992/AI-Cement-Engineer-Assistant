"""Data lineage and traceability system for cement production.

This module establishes the connected chain:
Raw_Materials → Raw_Mix → Kiln_Process → Clinker → Cement → Strength_Test → Standards

Each stage is connected via unique IDs, enabling full traceability and explainability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import uuid


@dataclass
class RawMaterial:
    """Represents a raw material source (limestone, silica sand, clay, iron ore, etc.)."""
    
    raw_material_id: str = field(default_factory=lambda: f"RM_{uuid.uuid4().hex[:8]}")
    name: str = ""
    material_type: str = ""  # e.g., "limestone", "silica_sand", "clay", "iron_ore"
    
    # Chemical composition (oxide percentages)
    cao_percent: float = 0.0
    sio2_percent: float = 0.0
    al2o3_percent: float = 0.0
    fe2o3_percent: float = 0.0
    mgo_percent: float = 0.0
    na2o_percent: float = 0.0
    k2o_percent: float = 0.0
    so3_percent: float = 0.0
    
    # Physical properties
    fineness_cm2_g: Optional[float] = None  # Blaine fineness
    moisture_percent: Optional[float] = None
    density_g_cm3: Optional[float] = None
    
    # Metadata
    source: str = ""
    lot_number: str = ""
    date_acquired: Optional[datetime] = None
    notes: str = ""
    
    def oxide_composition(self) -> Dict[str, float]:
        """Return oxide composition as dictionary."""
        return {
            "CaO": self.cao_percent,
            "SiO2": self.sio2_percent,
            "Al2O3": self.al2o3_percent,
            "Fe2O3": self.fe2o3_percent,
            "MgO": self.mgo_percent,
            "Na2O": self.na2o_percent,
            "K2O": self.k2o_percent,
            "SO3": self.so3_percent,
        }


@dataclass
class RawMix:
    """Represents a raw meal blend (combination of raw materials)."""
    
    raw_mix_id: str = field(default_factory=lambda: f"RM_{uuid.uuid4().hex[:8]}")
    
    # Links to input raw materials
    raw_materials: List[Dict] = field(default_factory=list)  # List of {"raw_material_id", "proportion_percent"}
    
    # Resulting oxide composition
    cao_percent: float = 0.0
    sio2_percent: float = 0.0
    al2o3_percent: float = 0.0
    fe2o3_percent: float = 0.0
    mgo_percent: float = 0.0
    
    # Clinker quality indices
    lsf: Optional[float] = None  # Lime Saturation Factor
    sm: Optional[float] = None   # Silica Modulus
    am: Optional[float] = None   # Alumina Modulus
    
    # Metadata
    date_created: datetime = field(default_factory=datetime.now)
    notes: str = ""
    
    def oxide_composition(self) -> Dict[str, float]:
        """Return oxide composition as dictionary."""
        return {
            "CaO": self.cao_percent,
            "SiO2": self.sio2_percent,
            "Al2O3": self.al2o3_percent,
            "Fe2O3": self.fe2o3_percent,
            "MgO": self.mgo_percent,
        }


@dataclass
class KilnRun:
    """Represents a single kiln firing/clinkerization run."""
    
    kiln_run_id: str = field(default_factory=lambda: f"KR_{uuid.uuid4().hex[:8]}")
    
    # Link to raw mix
    raw_mix_id: str = ""
    
    # Process parameters
    maximum_temperature_celsius: float = 0.0
    dwell_time_minutes: Optional[float] = None
    cooling_rate_celsius_per_hour: Optional[float] = None
    
    # Kiln conditions
    air_fuel_ratio: Optional[float] = None
    excess_oxygen_percent: Optional[float] = None
    co2_in_kiln_gas_percent: Optional[float] = None
    
    # Metadata
    date_executed: datetime = field(default_factory=datetime.now)
    kiln_name: str = ""
    fuel_type: str = ""
    operator_notes: str = ""
    
    # Quality feedback
    flame_appearance: str = ""  # e.g., "short", "medium", "long"
    dust_level: str = ""  # e.g., "low", "medium", "high"


@dataclass
class Clinker:
    """Represents the clinker product from a kiln run."""
    
    clinker_id: str = field(default_factory=lambda: f"CK_{uuid.uuid4().hex[:8]}")
    
    # Links to production process
    kiln_run_id: str = ""
    raw_mix_id: str = ""
    
    # Phase composition (from X-ray diffraction or calculation)
    c3s_percent: Optional[float] = None  # Alite (3CaO·SiO2)
    c2s_percent: Optional[float] = None  # Belite (2CaO·SiO2)
    c3a_percent: Optional[float] = None  # Aluminate (3CaO·Al2O3)
    c4af_percent: Optional[float] = None  # Ferrite (4CaO·Al2O3·Fe2O3)
    
    # Free lime
    free_cao_percent: float = 0.0
    
    # Oxide composition (measured)
    cao_percent: float = 0.0
    sio2_percent: float = 0.0
    al2o3_percent: float = 0.0
    fe2o3_percent: float = 0.0
    mgo_percent: float = 0.0
    
    # Physical properties
    fineness_cm2_g: Optional[float] = None  # Blaine fineness
    density_g_cm3: Optional[float] = None
    bulk_density_kg_m3: Optional[float] = None
    
    # Quality indices
    lsf: Optional[float] = None
    sm: Optional[float] = None
    am: Optional[float] = None
    
    # Metadata
    date_produced: datetime = field(default_factory=datetime.now)
    batch_number: str = ""
    storage_location: str = ""
    quality_rating: Optional[str] = None  # e.g., "premium", "standard", "reprocess"
    notes: str = ""
    
    def phase_composition(self) -> Dict[str, Optional[float]]:
        """Return phase composition as dictionary."""
        return {
            "C3S": self.c3s_percent,
            "C2S": self.c2s_percent,
            "C3A": self.c3a_percent,
            "C4AF": self.c4af_percent,
        }


@dataclass
class CementBatch:
    """Represents a cement batch (clinker + gypsum/additives ground together)."""
    
    cement_batch_id: str = field(default_factory=lambda: f"CB_{uuid.uuid4().hex[:8]}")
    
    # Links to source materials
    clinker_id: str = ""
    kiln_run_id: str = ""
    raw_mix_id: str = ""
    
    # Composition
    clinker_percent: float = 100.0
    gypsum_percent: float = 0.0
    pozzolan_percent: float = 0.0
    slag_percent: float = 0.0
    other_additives_percent: float = 0.0
    
    # Cement type
    cement_type: str = ""  # e.g., "OPC", "PPC", "PSC", "SRC"
    
    # Physical properties (after grinding)
    fineness_cm2_g: Optional[float] = None  # Blaine fineness
    density_g_cm3: Optional[float] = None
    bulk_density_kg_m3: Optional[float] = None
    
    # Chemical composition
    cao_percent: float = 0.0
    sio2_percent: float = 0.0
    al2o3_percent: float = 0.0
    fe2o3_percent: float = 0.0
    mgo_percent: float = 0.0
    so3_percent: float = 0.0
    na2o_percent: float = 0.0
    k2o_percent: float = 0.0
    
    # Metadata
    date_produced: datetime = field(default_factory=datetime.now)
    batch_number: str = ""
    grinding_duration_minutes: Optional[float] = None
    quality_rating: Optional[str] = None
    notes: str = ""


@dataclass
class StrengthTest:
    """Represents concrete strength test results."""
    
    strength_test_id: str = field(default_factory=lambda: f"ST_{uuid.uuid4().hex[:8]}")
    
    # Links to cement and production chain
    cement_batch_id: str = ""
    clinker_id: str = ""
    kiln_run_id: str = ""
    raw_mix_id: str = ""
    
    # Test metadata
    test_date: datetime = field(default_factory=datetime.now)
    casting_date: datetime = field(default_factory=datetime.now)
    specimen_type: str = ""  # e.g., "cube_150mm", "cylinder_100x200mm"
    curing_type: str = ""     # e.g., "water", "air", "steam"
    
    # Concrete mix design
    cement_kg_m3: float = 0.0
    water_kg_m3: float = 0.0
    fine_aggregate_kg_m3: float = 0.0
    coarse_aggregate_kg_m3: float = 0.0
    w_c_ratio: float = 0.0  # water-cement ratio
    
    # Strength results
    compressive_strength_7d_mpa: Optional[float] = None
    compressive_strength_28d_mpa: Optional[float] = None
    compressive_strength_90d_mpa: Optional[float] = None
    
    flexural_strength_28d_mpa: Optional[float] = None
    
    # Additional properties
    slump_mm: Optional[float] = None
    air_content_percent: Optional[float] = None
    
    # Metadata
    laboratory_id: str = ""
    technician_name: str = ""
    test_standard: str = ""  # e.g., "ASTM C39", "IS 516"
    notes: str = ""


@dataclass
class StandardCompliance:
    """Represents compliance with cement/concrete standards."""
    
    standard_id: str = field(default_factory=lambda: f"STD_{uuid.uuid4().hex[:8]}")
    
    # Links to cement and test results
    cement_batch_id: str = ""
    strength_test_id: Optional[str] = None
    
    # Standard references
    standard_name: str = ""  # e.g., "IS 269:2015", "EN 197-1:2011", "ASTM C150"
    standard_type: str = ""  # e.g., "33 Grade", "42.5 Grade", "Type I", "Type II"
    
    # Compliance checks (pass/fail)
    fineness_requirement_met: bool = True
    strength_28d_requirement_met: bool = True
    strength_7d_requirement_met: bool = True
    expansion_requirement_met: bool = True
    initial_setting_time_met: bool = True
    final_setting_time_met: bool = True
    false_set_requirement_met: bool = True
    
    # Measured properties
    measured_28d_strength_mpa: Optional[float] = None
    required_28d_strength_mpa: Optional[float] = None
    measured_fineness_cm2_g: Optional[float] = None
    required_fineness_cm2_g: Optional[float] = None
    
    # Status
    compliance_status: str = "pending"  # "passed", "failed", "conditional"
    test_date: datetime = field(default_factory=datetime.now)
    notes: str = ""


@dataclass
class LineageTrace:
    """Represents a complete traceability chain from raw materials to strength results."""
    
    trace_id: str = field(default_factory=lambda: f"TR_{uuid.uuid4().hex[:8]}")
    
    # The complete chain
    raw_materials: List[RawMaterial] = field(default_factory=list)
    raw_mix: Optional[RawMix] = None
    kiln_run: Optional[KilnRun] = None
    clinker: Optional[Clinker] = None
    cement_batch: Optional[CementBatch] = None
    strength_tests: List[StrengthTest] = field(default_factory=list)
    standards: List[StandardCompliance] = field(default_factory=list)
    
    def get_strength_trajectory(self) -> Dict[int, float]:
        """Return 28-day strength results across tests."""
        strengths = {}
        for test in self.strength_tests:
            if test.compressive_strength_28d_mpa is not None:
                strengths[test.strength_test_id] = test.compressive_strength_28d_mpa
        return strengths
    
    def get_raw_mix_composition_description(self) -> str:
        """Describe the raw mix composition and its influence on clinker."""
        if not self.raw_materials or not self.raw_mix:
            return "No raw mix data available"
        
        desc = "Raw materials blend:\n"
        for material in self.raw_materials:
            desc += f"  - {material.name} ({material.material_type}): CaO={material.cao_percent:.1f}%\n"
        
        desc += f"\nResulting raw mix:\n"
        desc += f"  - CaO: {self.raw_mix.cao_percent:.1f}%\n"
        desc += f"  - SiO2: {self.raw_mix.sio2_percent:.1f}%\n"
        desc += f"  - LSF: {self.raw_mix.lsf:.2f}\n" if self.raw_mix.lsf else ""
        
        return desc
    
    def get_clinker_quality_description(self) -> str:
        """Describe clinker quality and phase composition."""
        if not self.clinker:
            return "No clinker data available"
        
        desc = f"Clinker quality:\n"
        desc += f"  - Free CaO: {self.clinker.free_cao_percent:.2f}%\n"
        if self.clinker.c3s_percent is not None:
            desc += f"  - C3S (Alite): {self.clinker.c3s_percent:.1f}%\n"
        if self.clinker.c2s_percent is not None:
            desc += f"  - C2S (Belite): {self.clinker.c2s_percent:.1f}%\n"
        
        return desc
    
    def trace_strength_causality(self) -> str:
        """Generate a causal explanation for cement strength."""
        explanation = "Causal trace for cement strength:\n\n"
        
        # Step 1: Raw materials
        explanation += "1. RAW MATERIALS\n"
        explanation += self.get_raw_mix_composition_description() + "\n"
        
        # Step 2: Clinker quality
        explanation += "2. KILN PERFORMANCE & CLINKER QUALITY\n"
        explanation += self.get_clinker_quality_description() + "\n"
        
        # Step 3: Cement properties
        if self.cement_batch:
            explanation += "3. CEMENT BATCH\n"
            explanation += f"  - Type: {self.cement_batch.cement_type}\n"
            explanation += f"  - Fineness: {self.cement_batch.fineness_cm2_g:.0f} cm²/g\n"
            explanation += f"  - CaO: {self.cement_batch.cao_percent:.1f}%\n\n"
        
        # Step 4: Strength results
        explanation += "4. STRENGTH TEST RESULTS (28-day)\n"
        for test in self.strength_tests:
            if test.compressive_strength_28d_mpa is not None:
                explanation += f"  - {test.specimen_type}: {test.compressive_strength_28d_mpa:.1f} MPa\n"
        
        return explanation


# Helper function to load or create lineage traces from data files
def create_lineage_trace_from_ids(
    raw_material_ids: List[str],
    raw_mix_id: str,
    kiln_run_id: str,
    clinker_id: str,
    cement_batch_id: str,
    strength_test_ids: List[str] = None,
) -> LineageTrace:
    """Create a lineage trace structure connecting all production stages."""
    
    trace = LineageTrace()
    # In a real system, these would be loaded from a database
    # For now, this provides the structure template
    trace.raw_mix = RawMix(raw_mix_id=raw_mix_id)
    trace.kiln_run = KilnRun(kiln_run_id=kiln_run_id, raw_mix_id=raw_mix_id)
    trace.clinker = Clinker(clinker_id=clinker_id, kiln_run_id=kiln_run_id, raw_mix_id=raw_mix_id)
    trace.cement_batch = CementBatch(cement_batch_id=cement_batch_id, clinker_id=clinker_id)
    
    if strength_test_ids:
        for test_id in strength_test_ids:
            trace.strength_tests.append(
                StrengthTest(
                    strength_test_id=test_id,
                    cement_batch_id=cement_batch_id,
                    clinker_id=clinker_id,
                )
            )
    
    return trace
