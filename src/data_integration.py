"""Database schema and data integration for cement production lineage.

This module provides:
1. SQL schema for storing the connected data chain
2. Helper functions to load/save lineage data
3. Query functions to retrieve traces
"""

from __future__ import annotations

import sqlite3
from typing import List, Optional, Dict
from datetime import datetime
import json

from src.data_lineage import (
    RawMaterial,
    RawMix,
    KilnRun,
    Clinker,
    CementBatch,
    StrengthTest,
    StandardCompliance,
    LineageTrace,
)


# SQL Schema for the connected data chain
DATABASE_SCHEMA = """
-- Raw Materials table
CREATE TABLE IF NOT EXISTS raw_materials (
    raw_material_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    material_type TEXT,
    cao_percent REAL,
    sio2_percent REAL,
    al2o3_percent REAL,
    fe2o3_percent REAL,
    mgo_percent REAL,
    na2o_percent REAL,
    k2o_percent REAL,
    so3_percent REAL,
    fineness_cm2_g REAL,
    moisture_percent REAL,
    density_g_cm3 REAL,
    source TEXT,
    lot_number TEXT,
    date_acquired TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Raw Mix table (links to raw materials)
CREATE TABLE IF NOT EXISTS raw_mixes (
    raw_mix_id TEXT PRIMARY KEY,
    cao_percent REAL,
    sio2_percent REAL,
    al2o3_percent REAL,
    fe2o3_percent REAL,
    mgo_percent REAL,
    lsf REAL,
    sm REAL,
    am REAL,
    date_created TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Raw Mix Composition (many-to-many: which raw materials in which proportions)
CREATE TABLE IF NOT EXISTS raw_mix_composition (
    composition_id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_mix_id TEXT NOT NULL,
    raw_material_id TEXT NOT NULL,
    proportion_percent REAL,
    FOREIGN KEY (raw_mix_id) REFERENCES raw_mixes(raw_mix_id),
    FOREIGN KEY (raw_material_id) REFERENCES raw_materials(raw_material_id)
);

-- Kiln Run table (links to raw mix)
CREATE TABLE IF NOT EXISTS kiln_runs (
    kiln_run_id TEXT PRIMARY KEY,
    raw_mix_id TEXT NOT NULL,
    maximum_temperature_celsius REAL,
    dwell_time_minutes REAL,
    cooling_rate_celsius_per_hour REAL,
    air_fuel_ratio REAL,
    excess_oxygen_percent REAL,
    co2_in_kiln_gas_percent REAL,
    date_executed TIMESTAMP,
    kiln_name TEXT,
    fuel_type TEXT,
    operator_notes TEXT,
    flame_appearance TEXT,
    dust_level TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (raw_mix_id) REFERENCES raw_mixes(raw_mix_id)
);

-- Clinker table (links to kiln run and raw mix)
CREATE TABLE IF NOT EXISTS clinkers (
    clinker_id TEXT PRIMARY KEY,
    kiln_run_id TEXT NOT NULL,
    raw_mix_id TEXT NOT NULL,
    c3s_percent REAL,
    c2s_percent REAL,
    c3a_percent REAL,
    c4af_percent REAL,
    free_cao_percent REAL,
    cao_percent REAL,
    sio2_percent REAL,
    al2o3_percent REAL,
    fe2o3_percent REAL,
    mgo_percent REAL,
    fineness_cm2_g REAL,
    density_g_cm3 REAL,
    bulk_density_kg_m3 REAL,
    lsf REAL,
    sm REAL,
    am REAL,
    date_produced TIMESTAMP,
    batch_number TEXT,
    storage_location TEXT,
    quality_rating TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kiln_run_id) REFERENCES kiln_runs(kiln_run_id),
    FOREIGN KEY (raw_mix_id) REFERENCES raw_mixes(raw_mix_id)
);

-- Cement Batch table (links to clinker)
CREATE TABLE IF NOT EXISTS cement_batches (
    cement_batch_id TEXT PRIMARY KEY,
    clinker_id TEXT NOT NULL,
    kiln_run_id TEXT NOT NULL,
    raw_mix_id TEXT NOT NULL,
    clinker_percent REAL,
    gypsum_percent REAL,
    pozzolan_percent REAL,
    slag_percent REAL,
    other_additives_percent REAL,
    cement_type TEXT,
    fineness_cm2_g REAL,
    density_g_cm3 REAL,
    bulk_density_kg_m3 REAL,
    cao_percent REAL,
    sio2_percent REAL,
    al2o3_percent REAL,
    fe2o3_percent REAL,
    mgo_percent REAL,
    so3_percent REAL,
    na2o_percent REAL,
    k2o_percent REAL,
    date_produced TIMESTAMP,
    batch_number TEXT,
    grinding_duration_minutes REAL,
    quality_rating TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (clinker_id) REFERENCES clinkers(clinker_id),
    FOREIGN KEY (kiln_run_id) REFERENCES kiln_runs(kiln_run_id),
    FOREIGN KEY (raw_mix_id) REFERENCES raw_mixes(raw_mix_id)
);

-- Strength Test table (links to cement batch)
CREATE TABLE IF NOT EXISTS strength_tests (
    strength_test_id TEXT PRIMARY KEY,
    cement_batch_id TEXT NOT NULL,
    clinker_id TEXT NOT NULL,
    kiln_run_id TEXT NOT NULL,
    raw_mix_id TEXT NOT NULL,
    test_date TIMESTAMP,
    casting_date TIMESTAMP,
    specimen_type TEXT,
    curing_type TEXT,
    cement_kg_m3 REAL,
    water_kg_m3 REAL,
    fine_aggregate_kg_m3 REAL,
    coarse_aggregate_kg_m3 REAL,
    w_c_ratio REAL,
    compressive_strength_7d_mpa REAL,
    compressive_strength_28d_mpa REAL,
    compressive_strength_90d_mpa REAL,
    flexural_strength_28d_mpa REAL,
    slump_mm REAL,
    air_content_percent REAL,
    laboratory_id TEXT,
    technician_name TEXT,
    test_standard TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cement_batch_id) REFERENCES cement_batches(cement_batch_id),
    FOREIGN KEY (clinker_id) REFERENCES clinkers(clinker_id),
    FOREIGN KEY (kiln_run_id) REFERENCES kiln_runs(kiln_run_id),
    FOREIGN KEY (raw_mix_id) REFERENCES raw_mixes(raw_mix_id)
);

-- Standards Compliance table
CREATE TABLE IF NOT EXISTS standards_compliance (
    standard_id TEXT PRIMARY KEY,
    cement_batch_id TEXT NOT NULL,
    strength_test_id TEXT,
    standard_name TEXT,
    standard_type TEXT,
    fineness_requirement_met BOOLEAN,
    strength_28d_requirement_met BOOLEAN,
    strength_7d_requirement_met BOOLEAN,
    expansion_requirement_met BOOLEAN,
    initial_setting_time_met BOOLEAN,
    final_setting_time_met BOOLEAN,
    false_set_requirement_met BOOLEAN,
    measured_28d_strength_mpa REAL,
    required_28d_strength_mpa REAL,
    measured_fineness_cm2_g REAL,
    required_fineness_cm2_g REAL,
    compliance_status TEXT,
    test_date TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cement_batch_id) REFERENCES cement_batches(cement_batch_id),
    FOREIGN KEY (strength_test_id) REFERENCES strength_tests(strength_test_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_raw_mix_composition_raw_mix ON raw_mix_composition(raw_mix_id);
CREATE INDEX IF NOT EXISTS idx_kiln_runs_raw_mix ON kiln_runs(raw_mix_id);
CREATE INDEX IF NOT EXISTS idx_clinkers_kiln_run ON clinkers(kiln_run_id);
CREATE INDEX IF NOT EXISTS idx_clinkers_raw_mix ON clinkers(raw_mix_id);
CREATE INDEX IF NOT EXISTS idx_cement_batches_clinker ON cement_batches(clinker_id);
CREATE INDEX IF NOT EXISTS idx_strength_tests_cement_batch ON strength_tests(cement_batch_id);
CREATE INDEX IF NOT EXISTS idx_strength_tests_clinker ON strength_tests(clinker_id);
CREATE INDEX IF NOT EXISTS idx_standards_cement_batch ON standards_compliance(cement_batch_id);
"""


class LineageDatabase:
    """Database interface for cement production lineage."""
    
    def __init__(self, db_path: str = "cement_lineage.db"):
        """Initialize database connection and create schema."""
        self.db_path = db_path
        self.connection = None
        self.initialize_db()
    
    def initialize_db(self):
        """Create database and tables if they don't exist."""
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.cursor()
        
        # Split schema into individual statements and execute
        for statement in DATABASE_SCHEMA.split(";"):
            if statement.strip():
                cursor.execute(statement)
        
        self.connection.commit()
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
    
    def save_raw_material(self, material: RawMaterial) -> bool:
        """Save raw material to database."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO raw_materials 
                (raw_material_id, name, material_type, cao_percent, sio2_percent, 
                 al2o3_percent, fe2o3_percent, mgo_percent, na2o_percent, k2o_percent, 
                 so3_percent, fineness_cm2_g, moisture_percent, density_g_cm3,
                 source, lot_number, date_acquired, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                material.raw_material_id, material.name, material.material_type,
                material.cao_percent, material.sio2_percent, material.al2o3_percent,
                material.fe2o3_percent, material.mgo_percent, material.na2o_percent,
                material.k2o_percent, material.so3_percent, material.fineness_cm2_g,
                material.moisture_percent, material.density_g_cm3,
                material.source, material.lot_number, material.date_acquired, material.notes
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error saving raw material: {e}")
            return False
    
    def save_raw_mix(self, raw_mix: RawMix, material_links: Dict[str, float]) -> bool:
        """Save raw mix and its composition links."""
        cursor = self.connection.cursor()
        try:
            # Save raw mix
            cursor.execute("""
                INSERT OR REPLACE INTO raw_mixes
                (raw_mix_id, cao_percent, sio2_percent, al2o3_percent, fe2o3_percent,
                 mgo_percent, lsf, sm, am, date_created, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                raw_mix.raw_mix_id, raw_mix.cao_percent, raw_mix.sio2_percent,
                raw_mix.al2o3_percent, raw_mix.fe2o3_percent, raw_mix.mgo_percent,
                raw_mix.lsf, raw_mix.sm, raw_mix.am,
                raw_mix.date_created, raw_mix.notes
            ))
            
            # Save composition links
            for material_id, proportion in material_links.items():
                cursor.execute("""
                    INSERT INTO raw_mix_composition (raw_mix_id, raw_material_id, proportion_percent)
                    VALUES (?, ?, ?)
                """, (raw_mix.raw_mix_id, material_id, proportion))
            
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error saving raw mix: {e}")
            return False
    
    def save_kiln_run(self, kiln_run: KilnRun) -> bool:
        """Save kiln run to database."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO kiln_runs
                (kiln_run_id, raw_mix_id, maximum_temperature_celsius, dwell_time_minutes,
                 cooling_rate_celsius_per_hour, air_fuel_ratio, excess_oxygen_percent,
                 co2_in_kiln_gas_percent, date_executed, kiln_name, fuel_type,
                 operator_notes, flame_appearance, dust_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                kiln_run.kiln_run_id, kiln_run.raw_mix_id,
                kiln_run.maximum_temperature_celsius, kiln_run.dwell_time_minutes,
                kiln_run.cooling_rate_celsius_per_hour, kiln_run.air_fuel_ratio,
                kiln_run.excess_oxygen_percent, kiln_run.co2_in_kiln_gas_percent,
                kiln_run.date_executed, kiln_run.kiln_name, kiln_run.fuel_type,
                kiln_run.operator_notes, kiln_run.flame_appearance, kiln_run.dust_level
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error saving kiln run: {e}")
            return False
    
    def save_clinker(self, clinker: Clinker) -> bool:
        """Save clinker to database."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO clinkers
                (clinker_id, kiln_run_id, raw_mix_id, c3s_percent, c2s_percent, c3a_percent,
                 c4af_percent, free_cao_percent, cao_percent, sio2_percent, al2o3_percent,
                 fe2o3_percent, mgo_percent, fineness_cm2_g, density_g_cm3, bulk_density_kg_m3,
                 lsf, sm, am, date_produced, batch_number, storage_location, quality_rating, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                clinker.clinker_id, clinker.kiln_run_id, clinker.raw_mix_id,
                clinker.c3s_percent, clinker.c2s_percent, clinker.c3a_percent,
                clinker.c4af_percent, clinker.free_cao_percent,
                clinker.cao_percent, clinker.sio2_percent, clinker.al2o3_percent,
                clinker.fe2o3_percent, clinker.mgo_percent,
                clinker.fineness_cm2_g, clinker.density_g_cm3, clinker.bulk_density_kg_m3,
                clinker.lsf, clinker.sm, clinker.am,
                clinker.date_produced, clinker.batch_number, clinker.storage_location,
                clinker.quality_rating, clinker.notes
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error saving clinker: {e}")
            return False
    
    def save_cement_batch(self, cement_batch: CementBatch) -> bool:
        """Save cement batch to database."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO cement_batches
                (cement_batch_id, clinker_id, kiln_run_id, raw_mix_id,
                 clinker_percent, gypsum_percent, pozzolan_percent, slag_percent,
                 other_additives_percent, cement_type, fineness_cm2_g, density_g_cm3,
                 bulk_density_kg_m3, cao_percent, sio2_percent, al2o3_percent, fe2o3_percent,
                 mgo_percent, so3_percent, na2o_percent, k2o_percent,
                 date_produced, batch_number, grinding_duration_minutes, quality_rating, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cement_batch.cement_batch_id, cement_batch.clinker_id, cement_batch.kiln_run_id,
                cement_batch.raw_mix_id,
                cement_batch.clinker_percent, cement_batch.gypsum_percent,
                cement_batch.pozzolan_percent, cement_batch.slag_percent,
                cement_batch.other_additives_percent, cement_batch.cement_type,
                cement_batch.fineness_cm2_g, cement_batch.density_g_cm3,
                cement_batch.bulk_density_kg_m3,
                cement_batch.cao_percent, cement_batch.sio2_percent, cement_batch.al2o3_percent,
                cement_batch.fe2o3_percent, cement_batch.mgo_percent, cement_batch.so3_percent,
                cement_batch.na2o_percent, cement_batch.k2o_percent,
                cement_batch.date_produced, cement_batch.batch_number,
                cement_batch.grinding_duration_minutes, cement_batch.quality_rating, cement_batch.notes
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error saving cement batch: {e}")
            return False
    
    def save_strength_test(self, test: StrengthTest) -> bool:
        """Save strength test to database."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO strength_tests
                (strength_test_id, cement_batch_id, clinker_id, kiln_run_id, raw_mix_id,
                 test_date, casting_date, specimen_type, curing_type,
                 cement_kg_m3, water_kg_m3, fine_aggregate_kg_m3, coarse_aggregate_kg_m3,
                 w_c_ratio, compressive_strength_7d_mpa, compressive_strength_28d_mpa,
                 compressive_strength_90d_mpa, flexural_strength_28d_mpa, slump_mm,
                 air_content_percent, laboratory_id, technician_name, test_standard, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test.strength_test_id, test.cement_batch_id, test.clinker_id, test.kiln_run_id,
                test.raw_mix_id, test.test_date, test.casting_date, test.specimen_type,
                test.curing_type,
                test.cement_kg_m3, test.water_kg_m3, test.fine_aggregate_kg_m3,
                test.coarse_aggregate_kg_m3, test.w_c_ratio,
                test.compressive_strength_7d_mpa, test.compressive_strength_28d_mpa,
                test.compressive_strength_90d_mpa, test.flexural_strength_28d_mpa,
                test.slump_mm, test.air_content_percent,
                test.laboratory_id, test.technician_name, test.test_standard, test.notes
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error saving strength test: {e}")
            return False
    
    def load_lineage_trace(self, cement_batch_id: str) -> Optional[LineageTrace]:
        """Load a complete lineage trace starting from a cement batch."""
        cursor = self.connection.cursor()
        
        # Load cement batch
        cursor.execute("SELECT * FROM cement_batches WHERE cement_batch_id = ?", (cement_batch_id,))
        cement_row = cursor.fetchone()
        if not cement_row:
            return None
        
        trace = LineageTrace()
        
        # Load cement batch
        # (Implementation would convert row to CementBatch object)
        
        # Load clinker
        # Load kiln run
        # Load raw mix
        # Load raw materials
        # Load strength tests
        
        return trace
    
    def get_lineage_chain(self, cement_batch_id: str) -> Dict:
        """Get the complete lineage chain as a dictionary."""
        cursor = self.connection.cursor()
        
        # Fetch cement batch
        cursor.execute("""
            SELECT cement_batch_id, clinker_id, kiln_run_id, raw_mix_id, 
                   cement_type, fineness_cm2_g, cao_percent, date_produced
            FROM cement_batches
            WHERE cement_batch_id = ?
        """, (cement_batch_id,))
        cement = cursor.fetchone()
        if not cement:
            return {}
        
        cement_dict = {
            "cement_batch_id": cement[0],
            "cement_type": cement[4],
            "fineness_cm2_g": cement[5],
            "cao_percent": cement[6],
            "date_produced": cement[7],
        }
        
        # Fetch clinker
        clinker_id = cement[1]
        cursor.execute("""
            SELECT clinker_id, free_cao_percent, c3s_percent, c2s_percent,
                   date_produced, batch_number
            FROM clinkers
            WHERE clinker_id = ?
        """, (clinker_id,))
        clinker = cursor.fetchone()
        
        clinker_dict = {
            "clinker_id": clinker_id,
            "free_cao_percent": clinker[1] if clinker else None,
            "c3s_percent": clinker[2] if clinker else None,
            "c2s_percent": clinker[3] if clinker else None,
            "date_produced": clinker[4] if clinker else None,
        }
        
        # Fetch kiln run
        kiln_run_id = cement[2]
        cursor.execute("""
            SELECT kiln_run_id, maximum_temperature_celsius, dwell_time_minutes,
                   date_executed, kiln_name
            FROM kiln_runs
            WHERE kiln_run_id = ?
        """, (kiln_run_id,))
        kiln = cursor.fetchone()
        
        kiln_dict = {
            "kiln_run_id": kiln_run_id,
            "max_temp_celsius": kiln[1] if kiln else None,
            "dwell_time_minutes": kiln[2] if kiln else None,
            "date_executed": kiln[3] if kiln else None,
        }
        
        # Fetch raw mix
        raw_mix_id = cement[3]
        cursor.execute("""
            SELECT raw_mix_id, cao_percent, sio2_percent, lsf, sm
            FROM raw_mixes
            WHERE raw_mix_id = ?
        """, (raw_mix_id,))
        raw_mix = cursor.fetchone()
        
        raw_mix_dict = {
            "raw_mix_id": raw_mix_id,
            "cao_percent": raw_mix[1] if raw_mix else None,
            "sio2_percent": raw_mix[2] if raw_mix else None,
            "lsf": raw_mix[3] if raw_mix else None,
        }
        
        # Fetch raw materials
        cursor.execute("""
            SELECT rm.raw_material_id, rm.name, rm.material_type, 
                   rm.cao_percent, rm.sio2_percent, rmc.proportion_percent
            FROM raw_materials rm
            JOIN raw_mix_composition rmc ON rm.raw_material_id = rmc.raw_material_id
            WHERE rmc.raw_mix_id = ?
        """, (raw_mix_id,))
        raw_materials_list = cursor.fetchall()
        
        # Fetch strength tests
        cursor.execute("""
            SELECT strength_test_id, compressive_strength_28d_mpa, w_c_ratio, curing_type
            FROM strength_tests
            WHERE cement_batch_id = ?
        """, (cement_batch_id,))
        strength_tests = cursor.fetchall()
        
        return {
            "cement": cement_dict,
            "clinker": clinker_dict,
            "kiln_run": kiln_dict,
            "raw_mix": raw_mix_dict,
            "raw_materials": [
                {
                    "name": m[1],
                    "type": m[2],
                    "cao_percent": m[3],
                    "sio2_percent": m[4],
                    "proportion_percent": m[5],
                }
                for m in raw_materials_list
            ],
            "strength_tests": [
                {
                    "strength_test_id": t[0],
                    "strength_28d_mpa": t[1],
                    "w_c_ratio": t[2],
                    "curing_type": t[3],
                }
                for t in strength_tests
            ],
        }
