"""Example loaders for building the connected cement data chain.

This module demonstrates how to:
1. Load data from CSV or Excel files for each stage
2. Connect the stages via foreign keys
3. Build the lineage trace for ML training and explainability
"""

from __future__ import annotations

from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

from src.data_lineage import (
    RawMaterial,
    RawMix,
    KilnRun,
    Clinker,
    CementBatch,
    StrengthTest,
    LineageTrace,
)
from src.data_integration import LineageDatabase
from src.chemistry.clinker_chemistry import calculate_clinker_ratios


class DataChainBuilder:
    """Helper class to build the connected cement production chain."""
    
    def __init__(self, db_path: str = "cement_lineage.db"):
        """Initialize with database connection."""
        self.db = LineageDatabase(db_path)
    
    def load_raw_materials_from_csv(self, csv_path: str) -> List[RawMaterial]:
        """Load raw materials from CSV file.
        
        Expected CSV columns:
        raw_material_id, name, material_type, cao_percent, sio2_percent, 
        al2o3_percent, fe2o3_percent, mgo_percent, na2o_percent, k2o_percent, 
        so3_percent, fineness_cm2_g, moisture_percent, source, lot_number, date_acquired, notes
        """
        df = pd.read_csv(csv_path)
        materials = []
        
        for _, row in df.iterrows():
            material = RawMaterial(
                raw_material_id=str(row.get("raw_material_id", "")),
                name=str(row.get("name", "")),
                material_type=str(row.get("material_type", "")),
                cao_percent=float(row.get("cao_percent", 0.0)),
                sio2_percent=float(row.get("sio2_percent", 0.0)),
                al2o3_percent=float(row.get("al2o3_percent", 0.0)),
                fe2o3_percent=float(row.get("fe2o3_percent", 0.0)),
                mgo_percent=float(row.get("mgo_percent", 0.0)),
                na2o_percent=float(row.get("na2o_percent", 0.0)),
                k2o_percent=float(row.get("k2o_percent", 0.0)),
                so3_percent=float(row.get("so3_percent", 0.0)),
                fineness_cm2_g=float(row.get("fineness_cm2_g", 0.0)) if pd.notna(row.get("fineness_cm2_g")) else None,
                moisture_percent=float(row.get("moisture_percent", 0.0)) if pd.notna(row.get("moisture_percent")) else None,
                density_g_cm3=float(row.get("density_g_cm3", 0.0)) if pd.notna(row.get("density_g_cm3")) else None,
                source=str(row.get("source", "")),
                lot_number=str(row.get("lot_number", "")),
                date_acquired=pd.to_datetime(row.get("date_acquired")) if pd.notna(row.get("date_acquired")) else None,
                notes=str(row.get("notes", "")),
            )
            materials.append(material)
            self.db.save_raw_material(material)
        
        return materials
    
    def create_raw_mix_from_materials(
        self,
        raw_mix_id: str,
        material_proportions: Dict[str, float],
        materials: Dict[str, RawMaterial],
    ) -> RawMix:
        """Create a raw mix from material proportions.
        
        Args:
            raw_mix_id: Unique identifier for this raw mix
            material_proportions: Dict of {raw_material_id: proportion_percent}
            materials: Dict of {raw_material_id: RawMaterial object}
        
        Returns:
            RawMix object with calculated composition and quality indices
        """
        
        # Normalize proportions
        total_prop = sum(material_proportions.values())
        if total_prop == 0:
            raise ValueError("Material proportions must sum to > 0")
        
        normalized_props = {
            mid: prop / total_prop for mid, prop in material_proportions.items()
        }
        
        # Calculate oxide composition
        cao = sum(materials[mid].cao_percent * normalized_props[mid] for mid in normalized_props)
        sio2 = sum(materials[mid].sio2_percent * normalized_props[mid] for mid in normalized_props)
        al2o3 = sum(materials[mid].al2o3_percent * normalized_props[mid] for mid in normalized_props)
        fe2o3 = sum(materials[mid].fe2o3_percent * normalized_props[mid] for mid in normalized_props)
        mgo = sum(materials[mid].mgo_percent * normalized_props[mid] for mid in normalized_props)
        
        raw_mix = RawMix(
            raw_mix_id=raw_mix_id,
            cao_percent=cao,
            sio2_percent=sio2,
            al2o3_percent=al2o3,
            fe2o3_percent=fe2o3,
            mgo_percent=mgo,
        )
        
        # Calculate quality indices
        oxide_data = {
            "CaO": cao,
            "SiO2": sio2,
            "Al2O3": al2o3,
            "Fe2O3": fe2o3,
        }
        ratios = calculate_clinker_ratios(oxide_data)
        raw_mix.lsf = ratios.get("LSF")
        raw_mix.sm = ratios.get("SM")
        raw_mix.am = ratios.get("AM")
        
        # Save to database
        self.db.save_raw_mix(raw_mix, material_proportions)
        
        return raw_mix
    
    def create_kiln_run(
        self,
        kiln_run_id: str,
        raw_mix_id: str,
        maximum_temperature_celsius: float,
        dwell_time_minutes: Optional[float] = None,
        cooling_rate_celsius_per_hour: Optional[float] = None,
        kiln_name: str = "",
        fuel_type: str = "",
        **kwargs
    ) -> KilnRun:
        """Create a kiln run linked to a raw mix."""
        
        kiln_run = KilnRun(
            kiln_run_id=kiln_run_id,
            raw_mix_id=raw_mix_id,
            maximum_temperature_celsius=maximum_temperature_celsius,
            dwell_time_minutes=dwell_time_minutes,
            cooling_rate_celsius_per_hour=cooling_rate_celsius_per_hour,
            kiln_name=kiln_name,
            fuel_type=fuel_type,
            **kwargs
        )
        
        self.db.save_kiln_run(kiln_run)
        return kiln_run
    
    def create_clinker(
        self,
        clinker_id: str,
        kiln_run_id: str,
        raw_mix_id: str,
        c3s_percent: Optional[float] = None,
        c2s_percent: Optional[float] = None,
        c3a_percent: Optional[float] = None,
        c4af_percent: Optional[float] = None,
        free_cao_percent: float = 0.0,
        cao_percent: float = 0.0,
        sio2_percent: float = 0.0,
        al2o3_percent: float = 0.0,
        fe2o3_percent: float = 0.0,
        **kwargs
    ) -> Clinker:
        """Create clinker linked to kiln run and raw mix."""
        
        clinker = Clinker(
            clinker_id=clinker_id,
            kiln_run_id=kiln_run_id,
            raw_mix_id=raw_mix_id,
            c3s_percent=c3s_percent,
            c2s_percent=c2s_percent,
            c3a_percent=c3a_percent,
            c4af_percent=c4af_percent,
            free_cao_percent=free_cao_percent,
            cao_percent=cao_percent,
            sio2_percent=sio2_percent,
            al2o3_percent=al2o3_percent,
            fe2o3_percent=fe2o3_percent,
            **kwargs
        )
        
        # Calculate quality indices if not provided
        if clinker.lsf is None:
            oxide_data = {
                "CaO": cao_percent,
                "SiO2": sio2_percent,
                "Al2O3": al2o3_percent,
                "Fe2O3": fe2o3_percent,
            }
            ratios = calculate_clinker_ratios(oxide_data)
            clinker.lsf = ratios.get("LSF")
            clinker.sm = ratios.get("SM")
            clinker.am = ratios.get("AM")
        
        self.db.save_clinker(clinker)
        return clinker
    
    def create_cement_batch(
        self,
        cement_batch_id: str,
        clinker_id: str,
        kiln_run_id: str,
        raw_mix_id: str,
        cement_type: str = "OPC",
        clinker_percent: float = 95.0,
        gypsum_percent: float = 5.0,
        fineness_cm2_g: Optional[float] = None,
        **kwargs
    ) -> CementBatch:
        """Create cement batch linked to clinker."""
        
        cement_batch = CementBatch(
            cement_batch_id=cement_batch_id,
            clinker_id=clinker_id,
            kiln_run_id=kiln_run_id,
            raw_mix_id=raw_mix_id,
            cement_type=cement_type,
            clinker_percent=clinker_percent,
            gypsum_percent=gypsum_percent,
            fineness_cm2_g=fineness_cm2_g,
            **kwargs
        )
        
        self.db.save_cement_batch(cement_batch)
        return cement_batch
    
    def create_strength_test(
        self,
        strength_test_id: str,
        cement_batch_id: str,
        clinker_id: str,
        kiln_run_id: str,
        raw_mix_id: str,
        w_c_ratio: float,
        compressive_strength_28d_mpa: Optional[float] = None,
        **kwargs
    ) -> StrengthTest:
        """Create strength test linked to cement batch."""
        
        test = StrengthTest(
            strength_test_id=strength_test_id,
            cement_batch_id=cement_batch_id,
            clinker_id=clinker_id,
            kiln_run_id=kiln_run_id,
            raw_mix_id=raw_mix_id,
            w_c_ratio=w_c_ratio,
            compressive_strength_28d_mpa=compressive_strength_28d_mpa,
            **kwargs
        )
        
        self.db.save_strength_test(test)
        return test
    
    def build_complete_lineage(
        self,
        raw_material_ids: List[str],
        raw_mix_id: str,
        kiln_run_id: str,
        clinker_id: str,
        cement_batch_id: str,
        strength_test_ids: List[str] = None,
    ) -> LineageTrace:
        """Build a complete lineage trace from database."""
        
        # This is a template for how the complete trace would be built
        trace = LineageTrace()
        
        # In a real implementation, would load from database
        # For now, provides the structure
        
        return trace


def example_create_data_chain():
    """Example showing how to create the complete connected data chain."""
    
    builder = DataChainBuilder(db_path="cement_lineage_example.db")
    
    # Step 1: Define raw materials
    limestone = RawMaterial(
        raw_material_id="RM_001",
        name="Limestone",
        material_type="limestone",
        cao_percent=52.0,
        sio2_percent=2.5,
        al2o3_percent=1.2,
        fe2o3_percent=0.3,
        mgo_percent=1.8,
        source="Quarry A",
        lot_number="L202301",
    )
    
    silica_sand = RawMaterial(
        raw_material_id="RM_002",
        name="Silica Sand",
        material_type="silica_sand",
        cao_percent=1.0,
        sio2_percent=92.0,
        al2o3_percent=3.5,
        fe2o3_percent=1.5,
        mgo_percent=0.5,
        source="Quarry B",
        lot_number="S202301",
    )
    
    clay = RawMaterial(
        raw_material_id="RM_003",
        name="Clay",
        material_type="clay",
        cao_percent=2.0,
        sio2_percent=65.0,
        al2o3_percent=22.0,
        fe2o3_percent=8.0,
        mgo_percent=1.5,
        source="Quarry C",
        lot_number="C202301",
    )
    
    builder.db.save_raw_material(limestone)
    builder.db.save_raw_material(silica_sand)
    builder.db.save_raw_material(clay)
    
    # Step 2: Create raw mix from proportions
    raw_mix = builder.create_raw_mix_from_materials(
        raw_mix_id="RM_001",
        material_proportions={
            "RM_001": 70.0,  # 70% limestone
            "RM_002": 20.0,  # 20% silica sand
            "RM_003": 10.0,  # 10% clay
        },
        materials={
            "RM_001": limestone,
            "RM_002": silica_sand,
            "RM_003": clay,
        }
    )
    
    print(f"Raw Mix Created: {raw_mix.raw_mix_id}")
    print(f"  CaO: {raw_mix.cao_percent:.1f}%, SiO2: {raw_mix.sio2_percent:.1f}%")
    print(f"  LSF: {raw_mix.lsf:.2f}, SM: {raw_mix.sm:.2f}\n")
    
    # Step 3: Create kiln run
    kiln_run = builder.create_kiln_run(
        kiln_run_id="KR_001",
        raw_mix_id=raw_mix.raw_mix_id,
        maximum_temperature_celsius=1480,
        dwell_time_minutes=25,
        cooling_rate_celsius_per_hour=50,
        kiln_name="Kiln_A",
        fuel_type="Coal",
    )
    
    print(f"Kiln Run Created: {kiln_run.kiln_run_id}")
    print(f"  Temperature: {kiln_run.maximum_temperature_celsius}°C")
    print(f"  Dwell time: {kiln_run.dwell_time_minutes} min\n")
    
    # Step 4: Create clinker
    clinker = builder.create_clinker(
        clinker_id="CK_001",
        kiln_run_id=kiln_run.kiln_run_id,
        raw_mix_id=raw_mix.raw_mix_id,
        c3s_percent=65.0,  # High alite content
        c2s_percent=20.0,
        c3a_percent=8.0,
        c4af_percent=9.0,
        free_cao_percent=1.5,
        cao_percent=64.0,
        sio2_percent=21.0,
        al2o3_percent=5.5,
        fe2o3_percent=3.5,
    )
    
    print(f"Clinker Created: {clinker.clinker_id}")
    print(f"  C3S (Alite): {clinker.c3s_percent:.1f}% - HIGH strength potential")
    print(f"  Free CaO: {clinker.free_cao_percent:.1f}%\n")
    
    # Step 5: Create cement batch
    cement = builder.create_cement_batch(
        cement_batch_id="CB_001",
        clinker_id=clinker.clinker_id,
        kiln_run_id=kiln_run.kiln_run_id,
        raw_mix_id=raw_mix.raw_mix_id,
        cement_type="OPC",
        clinker_percent=95.0,
        gypsum_percent=5.0,
        fineness_cm2_g=3500,  # Good fineness
    )
    
    print(f"Cement Batch Created: {cement.cement_batch_id}")
    print(f"  Type: {cement.cement_type}")
    print(f"  Fineness: {cement.fineness_cm2_g} cm²/g\n")
    
    # Step 6: Create strength test
    strength_test = builder.create_strength_test(
        strength_test_id="ST_001",
        cement_batch_id=cement.cement_batch_id,
        clinker_id=clinker.clinker_id,
        kiln_run_id=kiln_run.kiln_run_id,
        raw_mix_id=raw_mix.raw_mix_id,
        w_c_ratio=0.45,  # Good W/C ratio
        compressive_strength_28d_mpa=45.0,  # Strong result
        specimen_type="cube_150mm",
        curing_type="water",
    )
    
    print(f"Strength Test Created: {strength_test.strength_test_id}")
    print(f"  28-day Strength: {strength_test.compressive_strength_28d_mpa:.1f} MPa")
    print(f"  W/C Ratio: {strength_test.w_c_ratio:.2f}\n")
    
    # Step 7: Get lineage chain
    chain = builder.db.get_lineage_chain(cement.cement_batch_id)
    
    print("=" * 70)
    print("COMPLETE LINEAGE CHAIN")
    print("=" * 70)
    print(f"\nRaw Materials: {[m['name'] for m in chain.get('raw_materials', [])]}")
    print(f"Raw Mix LSF: {chain['raw_mix'].get('lsf'):.2f}")
    print(f"Kiln Temperature: {chain['kiln_run'].get('max_temp_celsius')}°C")
    print(f"Clinker Alite (C3S): {chain['clinker'].get('c3s_percent'):.1f}%")
    print(f"Cement Fineness: {chain['cement'].get('fineness_cm2_g')} cm²/g")
    print(f"28-day Strength: {chain['strength_tests'][0].get('strength_28d_mpa'):.1f} MPa")
    
    builder.db.close()


if __name__ == "__main__":
    example_create_data_chain()
