#!/usr/bin/env python3
"""
Practical example demonstrating the cement production lineage system.

This script shows:
1. Creating a complete data chain (raw materials → strength)
2. Tracing backward to explain strength results
3. Identifying areas for improvement
"""

from datetime import datetime
from src.data_lineage import (
    RawMaterial, RawMix, KilnRun, Clinker, CementBatch, 
    StrengthTest, LineageTrace
)
from src.data_chain_loader import DataChainBuilder
from src.explainability.strength_explainer import StrengthExplainer
from src.data_integration import LineageDatabase


def main():
    """Run a complete end-to-end example."""
    
    print("=" * 80)
    print("CEMENT PRODUCTION LINEAGE & STRENGTH CAUSALITY ANALYSIS")
    print("=" * 80)
    print()
    
    # =========================================================================
    # PART 1: CREATE THE DATA CHAIN
    # =========================================================================
    print("PART 1: Building Complete Production Data Chain")
    print("-" * 80)
    
    builder = DataChainBuilder(db_path="cement_lineage_demo.db")
    
    # Define raw materials
    print("\n1. Defining Raw Materials...")
    
    limestone = RawMaterial(
        raw_material_id="RM_001",
        name="Limestone",
        material_type="limestone",
        cao_percent=52.0,
        sio2_percent=2.5,
        al2o3_percent=1.2,
        fe2o3_percent=0.3,
        mgo_percent=1.8,
        na2o_percent=0.0,
        k2o_percent=0.0,
        so3_percent=0.0,
        fineness_cm2_g=1200.0,
        moisture_percent=2.0,
        source="Limestone Quarry A",
        lot_number="L202401",
        date_acquired=datetime(2024, 1, 15),
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
        na2o_percent=0.5,
        k2o_percent=0.5,
        so3_percent=0.0,
        fineness_cm2_g=2500.0,
        moisture_percent=0.5,
        source="Silica Quarry B",
        lot_number="S202401",
        date_acquired=datetime(2024, 1, 20),
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
        na2o_percent=1.0,
        k2o_percent=2.0,
        so3_percent=0.0,
        fineness_cm2_g=800.0,
        moisture_percent=8.0,
        source="Clay Quarry C",
        lot_number="C202401",
        date_acquired=datetime(2024, 1, 25),
    )
    
    builder.db.save_raw_material(limestone)
    builder.db.save_raw_material(silica_sand)
    builder.db.save_raw_material(clay)
    
    print(f"   ✓ Limestone: CaO={limestone.cao_percent}%, SiO2={limestone.sio2_percent}%")
    print(f"   ✓ Silica Sand: SiO2={silica_sand.sio2_percent}%")
    print(f"   ✓ Clay: Al2O3={clay.al2o3_percent}%")
    
    # Create raw mix
    print("\n2. Creating Raw Mix from material proportions...")
    
    raw_mix = builder.create_raw_mix_from_materials(
        raw_mix_id="RM_001",
        material_proportions={
            "RM_001": 70.0,   # 70% limestone
            "RM_002": 20.0,   # 20% silica sand
            "RM_003": 10.0,   # 10% clay
        },
        materials={
            "RM_001": limestone,
            "RM_002": silica_sand,
            "RM_003": clay,
        }
    )
    
    print(f"   ✓ Raw Mix ID: {raw_mix.raw_mix_id}")
    print(f"     • CaO: {raw_mix.cao_percent:.2f}%")
    print(f"     • SiO2: {raw_mix.sio2_percent:.2f}%")
    print(f"     • LSF (Lime Saturation Factor): {raw_mix.lsf:.3f} (Target: 0.95-1.05)")
    print(f"     • SM (Silica Modulus): {raw_mix.sm:.2f} (Target: 2.3-3.0)")
    print(f"     • AM (Alumina Modulus): {raw_mix.am:.2f} (Target: 2.0-3.0)")
    
    # Create kiln run
    print("\n3. Creating Kiln Run...")
    
    kiln_run = builder.create_kiln_run(
        kiln_run_id="KR_001",
        raw_mix_id=raw_mix.raw_mix_id,
        maximum_temperature_celsius=1480,
        dwell_time_minutes=25,
        cooling_rate_celsius_per_hour=50,
        air_fuel_ratio=2.5,
        excess_oxygen_percent=2.5,
        co2_in_kiln_gas_percent=8.0,
        kiln_name="Kiln_A",
        fuel_type="Coal",
        operator_notes="Normal operation, stable flame",
        flame_appearance="medium",
        dust_level="low",
    )
    
    print(f"   ✓ Kiln Run ID: {kiln_run.kiln_run_id}")
    print(f"     • Max Temperature: {kiln_run.maximum_temperature_celsius}°C (Typical: 1450-1500°C)")
    print(f"     • Dwell Time: {kiln_run.dwell_time_minutes} min")
    print(f"     • Cooling Rate: {kiln_run.cooling_rate_celsius_per_hour}°C/hour")
    print(f"     • Status: {kiln_run.operator_notes}")
    
    # Create clinker
    print("\n4. Creating Clinker (XRD measured phase composition)...")
    
    clinker = builder.create_clinker(
        clinker_id="CK_001",
        kiln_run_id=kiln_run.kiln_run_id,
        raw_mix_id=raw_mix.raw_mix_id,
        c3s_percent=65.0,   # High alite = early strength
        c2s_percent=18.0,
        c3a_percent=8.5,
        c4af_percent=9.0,
        free_cao_percent=1.2,  # Low free CaO = good quality
        cao_percent=64.5,
        sio2_percent=20.8,
        al2o3_percent=5.2,
        fe2o3_percent=3.4,
        fineness_cm2_g=3200.0,
        date_produced=datetime(2024, 2, 1),
        batch_number="CK_202402_001",
        storage_location="Warehouse A",
        quality_rating="premium",
    )
    
    print(f"   ✓ Clinker ID: {clinker.clinker_id}")
    print(f"     • C3S (Alite): {clinker.c3s_percent}% - HIGH EARLY STRENGTH")
    print(f"     • C2S (Belite): {clinker.c2s_percent}% - late strength")
    print(f"     • C3A (Aluminate): {clinker.c3a_percent}%")
    print(f"     • C4AF (Ferrite): {clinker.c4af_percent}%")
    print(f"     • Free CaO: {clinker.free_cao_percent}% (Target: <2.5%)")
    print(f"     • Quality Rating: {clinker.quality_rating}")
    
    # Create cement batch
    print("\n5. Creating Cement Batch (clinker + gypsum grinding)...")
    
    cement = builder.create_cement_batch(
        cement_batch_id="CB_001",
        clinker_id=clinker.clinker_id,
        kiln_run_id=kiln_run.kiln_run_id,
        raw_mix_id=raw_mix.raw_mix_id,
        cement_type="OPC",
        clinker_percent=95.0,
        gypsum_percent=5.0,
        pozzolan_percent=0.0,
        slag_percent=0.0,
        fineness_cm2_g=3600.0,  # Good fineness = faster hydration
        density_g_cm3=3.14,
        bulk_density_kg_m3=1520.0,
        cao_percent=64.0,
        sio2_percent=20.5,
        al2o3_percent=5.0,
        fe2o3_percent=3.3,
        mgo_percent=2.5,
        so3_percent=3.0,
        date_produced=datetime(2024, 2, 5),
        batch_number="CB_202402_001",
        grinding_duration_minutes=90,
        quality_rating="standard",
    )
    
    print(f"   ✓ Cement Batch ID: {cement.cement_batch_id}")
    print(f"     • Type: {cement.cement_type}")
    print(f"     • Composition: {cement.clinker_percent}% clinker, {cement.gypsum_percent}% gypsum")
    print(f"     • Fineness: {cement.fineness_cm2_g} cm²/g (Higher = faster hydration)")
    print(f"     • Grinding Time: {cement.grinding_duration_minutes} min")
    
    # Create strength test
    print("\n6. Creating Strength Test (concrete performance)...")
    
    test = builder.create_strength_test(
        strength_test_id="ST_001",
        cement_batch_id=cement.cement_batch_id,
        clinker_id=clinker.clinker_id,
        kiln_run_id=kiln_run.kiln_run_id,
        raw_mix_id=raw_mix.raw_mix_id,
        specimen_type="cube_150mm",
        curing_type="water",
        cement_kg_m3=450.0,
        water_kg_m3=202.5,  # For W/C = 0.45
        fine_aggregate_kg_m3=630.0,
        coarse_aggregate_kg_m3=1260.0,
        w_c_ratio=0.45,  # Optimal W/C ratio
        compressive_strength_7d_mpa=32.5,
        compressive_strength_28d_mpa=48.2,  # Strong result!
        compressive_strength_90d_mpa=56.1,
        flexural_strength_28d_mpa=6.2,
        slump_mm=120.0,
        air_content_percent=2.0,
        test_date=datetime(2024, 3, 5),
        casting_date=datetime(2024, 2, 5),
        laboratory_id="Lab_001",
        technician_name="John Smith",
        test_standard="ASTM C39",
    )
    
    print(f"   ✓ Strength Test ID: {test.strength_test_id}")
    print(f"     • Mix Design: {test.cement_kg_m3} kg/m³ cement, W/C = {test.w_c_ratio}")
    print(f"     • 7-day Strength: {test.compressive_strength_7d_mpa} MPa")
    print(f"     • 28-day Strength: {test.compressive_strength_28d_mpa} MPa ← EXCELLENT")
    print(f"     • 90-day Strength: {test.compressive_strength_90d_mpa} MPa")
    print(f"     • Curing: {test.curing_type}, Slump: {test.slump_mm} mm")
    
    # =========================================================================
    # PART 2: QUERY THE CONNECTED CHAIN
    # =========================================================================
    print("\n" + "=" * 80)
    print("PART 2: Retrieving Complete Production Chain")
    print("-" * 80)
    
    db = LineageDatabase("cement_lineage_demo.db")
    chain_data = db.get_lineage_chain(cement.cement_batch_id)
    
    print("\nComplete Traceability Chain:")
    print(f"\nRaw Materials ({len(chain_data['raw_materials'])} materials):")
    for mat in chain_data['raw_materials']:
        print(f"  • {mat['name']} ({mat['type']}, {mat['proportion_percent']:.1f}%)")
        print(f"    CaO={mat['cao_percent']:.1f}%, SiO2={mat['sio2_percent']:.1f}%")
    
    print(f"\nRaw Mix:")
    print(f"  • CaO: {chain_data['raw_mix']['cao_percent']:.2f}%")
    print(f"  • LSF: {chain_data['raw_mix']['lsf']:.3f}")
    
    print(f"\nKiln Run:")
    print(f"  • Temperature: {chain_data['kiln_run']['max_temp_celsius']}°C")
    print(f"  • Dwell: {chain_data['kiln_run']['dwell_time_minutes']} min")
    
    print(f"\nClinker:")
    print(f"  • C3S: {chain_data['clinker']['c3s_percent']:.1f}%")
    print(f"  • Free CaO: {chain_data['clinker']['free_cao_percent']:.2f}%")
    
    print(f"\nCement:")
    print(f"  • Type: OPC")
    print(f"  • Fineness: {chain_data['cement']['fineness_cm2_g']} cm²/g")
    
    print(f"\nStrength Tests:")
    for test_data in chain_data['strength_tests']:
        print(f"  • 28-day: {test_data['strength_28d_mpa']:.1f} MPa (W/C={test_data['w_c_ratio']:.2f})")
    
    # =========================================================================
    # PART 3: EXPLAIN THE STRENGTH RESULT
    # =========================================================================
    print("\n" + "=" * 80)
    print("PART 3: Explaining the Strength Result (Root Cause Analysis)")
    print("-" * 80)
    
    # Create lineage trace
    trace = LineageTrace()
    trace.raw_materials = [limestone, silica_sand, clay]
    trace.raw_mix = raw_mix
    trace.kiln_run = kiln_run
    trace.clinker = clinker
    trace.cement_batch = cement
    trace.strength_tests = [test]
    
    # Create explainer
    explainer = StrengthExplainer(trace)
    
    # Generate explanation
    explanation = explainer.explain_strength_result(
        observed_strength_mpa=test.compressive_strength_28d_mpa
    )
    print("\n" + explanation)
    
    # Get factor importance
    print("\n" + "-" * 80)
    print("Factor Importance Ranking:")
    print("-" * 80)
    
    ranking = explainer.get_factor_importance_ranking()
    for i, (factor, importance, description) in enumerate(ranking[:5], 1):
        print(f"\n{i}. {factor.value.upper()}")
        print(f"   Importance: {importance:.2f}")
        print(f"   {description}")
    
    # Get recommendations
    print("\n" + "-" * 80)
    print("Improvement Recommendations:")
    print("-" * 80)
    
    recommendations = explainer.get_recommendations()
    if recommendations:
        for rec in recommendations:
            print(f"  ⚠ {rec}")
    else:
        print("  ✓ All factors within specification - excellent production!")
    
    # =========================================================================
    # CLEANUP
    # =========================================================================
    print("\n" + "=" * 80)
    print("Example complete! Database saved as: cement_lineage_demo.db")
    print("=" * 80)
    
    builder.db.close()
    db.close()


if __name__ == "__main__":
    main()
