import importlib.util
import math
import os
import pandas as pd
import pytest

# Load modules by file path to avoid importing package-level `src` which has heavy side-effects
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
SRC_ROOT = os.path.join(ROOT, "src", "chemistry")

def _load(name: str):
    path = os.path.join(SRC_ROOT, f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

ce = _load("chemistry_engine")
rm = _load("raw_mix")
ck = _load("clinker_chemistry")


def _build_materials_df():
    data = [
        {"Material_ID": "MAT005", "CaO": 43.50, "SiO2": 2.96, "Al2O3": 1.30, "Fe2O3": 0.80, "MgO": 4.00, "LOI": 44.35},
        {"Material_ID": "MAT011", "CaO": 3.00, "SiO2": 55.00, "Al2O3": 18.00, "Fe2O3": 6.50, "MgO": 2.00, "LOI": 10.00},
        {"Material_ID": "MAT009", "CaO": 1.50, "SiO2": 5.00, "Al2O3": 3.50, "Fe2O3": 85.00, "MgO": 0.50, "LOI": 4.00},
        {"Material_ID": "MAT010", "CaO": 0.50, "SiO2": 92.00, "Al2O3": 2.00, "Fe2O3": 1.00, "MgO": 0.20, "LOI": 1.50},
        {"Material_ID": "MAT006", "CaO": 42.00, "SiO2": 14.00, "Al2O3": 1.50, "Fe2O3": 1.50, "MgO": 3.50, "LOI": 37.50},
        {"Material_ID": "MAT007", "CaO": 2.50, "SiO2": 59.38, "Al2O3": 25.00, "Fe2O3": 7.00, "MgO": 1.10, "LOI": 4.50},
        {"Material_ID": "MAT008", "CaO": 33.50, "SiO2": 33.00, "Al2O3": 20.00, "Fe2O3": 0.60, "MgO": 8.50, "LOI": 0.00},
    ]
    return pd.DataFrame(data)


def almost_equal(a, b, tol=0.2):
    return abs(a - b) <= tol


def test_valid_100_percent_raw_mix():
    df = _build_materials_df()
    mix = {"MAT005": 86.5, "MAT011": 10.0, "MAT009": 1.5, "MAT010": 2.0}

    res = ce.calculate_raw_mix_chemistry(df, mix, basis="as_received")
    expected = rm.compute_weighted_oxides(df, mix)

    assert res["basis"] == "as_received"
    assert almost_equal(res["oxides"]["CaO"], expected["CaO"], tol=0.1)
    assert almost_equal(res["oxides"]["SiO2"], expected["SiO2"], tol=0.1)
    assert "mass_balance_sum" in res


def test_proportions_not_equal_100():
    df = _build_materials_df()
    mix = {"MAT005": 50.0, "MAT011": 20.0}  # sums to 70
    with pytest.raises(ValueError):
        ce.calculate_raw_mix_chemistry(df, mix, basis="as_received")


def test_negative_proportions():
    df = _build_materials_df()
    mix = {"MAT005": 80.0, "MAT011": -20.0}
    with pytest.raises(ValueError):
        ce.calculate_raw_mix_chemistry(df, mix, basis="as_received")


def test_missing_oxide_values():
    df = _build_materials_df()
    # remove CaO for MAT011
    df.loc[df.Material_ID == "MAT011", "CaO"] = float("nan")
    mix = {"MAT005": 86.5, "MAT011": 10.0, "MAT009": 1.5, "MAT010": 2.0}

    res = ce.calculate_raw_mix_chemistry(df, mix, basis="as_received")
    assert any("Missing oxide values" in w for w in res["warnings"]) or any(k for k, v in res["oxides"].items() if isinstance(v, float) and math.isnan(v))


def test_invalid_basis():
    df = _build_materials_df()
    mix = {"MAT005": 86.5, "MAT011": 10.0, "MAT009": 1.5, "MAT010": 2.0}
    with pytest.raises(ValueError):
        ce.calculate_raw_mix_chemistry(df, mix, basis="unknown_basis")


def test_as_received_basis_behavior():
    df = _build_materials_df()
    mix = {"MAT006": 82.0, "MAT007": 12.0, "MAT008": 5.0, "MAT009": 1.0}
    res = ce.calculate_raw_mix_chemistry(df, mix, basis="as_received")
    expected = rm.compute_weighted_oxides(df, mix)
    assert almost_equal(res["oxides"]["CaO"], expected["CaO"], tol=0.05)


def test_dry_basis_no_moisture_warns():
    df = _build_materials_df()
    mix = {"MAT006": 82.0, "MAT007": 12.0, "MAT008": 5.0, "MAT009": 1.0}
    res = ce.calculate_raw_mix_chemistry(df, mix, basis="dry")
    assert any("no moisture" in w.lower() for w in res["warnings"]) or res["basis"] == "dry"


def test_ignited_basis_conversion_and_moduli():
    df = _build_materials_df()
    mix = {"MAT005": 86.5, "MAT011": 10.0, "MAT009": 1.5, "MAT010": 2.0}
    res = ce.calculate_raw_mix_chemistry(df, mix, basis="ignited")
    # compare ignited conversion and moduli to raw_mix helpers
    raw = rm.compute_weighted_oxides(df, mix)
    ign, mult = rm.ignited_basis(raw)
    mods = rm.compute_moduli(ign)
    assert almost_equal(res["oxides_ignited"]["CaO"], ign["CaO"], tol=0.1)
    assert math.isclose(res["LSF"], mods["LSF"], rel_tol=1e-3)


def test_lsf_sm_am_wrappers():
    # Use ignited example values
    lsf = ce.calculate_lsf(62.67, 16.48, 3.01, 2.64, basis="ignited")
    assert math.isclose(lsf, ck.calculate_lsf(62.67, 16.48, 3.01, 2.64), rel_tol=1e-6)

    sm = ce.calculate_sm(16.48, 3.01, 2.64, basis="ignited")
    assert math.isclose(sm, ck.calculate_sm(16.48, 3.01, 2.64), rel_tol=1e-6)

    am = ce.calculate_am(3.01, 2.64, basis="ignited")
    assert math.isclose(am, ck.calculate_am(3.01, 2.64), rel_tol=1e-6)


def test_mass_balance_and_div_by_zero_protection():
    # Create a materials set that causes denominator zero for SM/AM
    df = pd.DataFrame([
        {"Material_ID": "A", "CaO": 50.0, "SiO2": 0.0, "Al2O3": 0.0, "Fe2O3": 0.0, "LOI": 0.0}
    ])
    mix = {"A": 100.0}
    res = ce.calculate_raw_mix_chemistry(df, mix, basis="as_received")
    # SM and AM cannot be computed -> should be NaN
    assert res["SM"] is None or (isinstance(res["SM"], float) and (math.isnan(res["SM"]) or res["SM"] == float("nan")))


def test_compatibility_with_existing_functions():
    # round-trip: compute raw mix ignited -> call calculate_lsf wrapper
    df = _build_materials_df()
    mix = {"MAT005": 86.5, "MAT011": 10.0, "MAT009": 1.5, "MAT010": 2.0}
    res = ce.calculate_raw_mix_chemistry(df, mix, basis="ignited")
    ign = res.get("oxides_ignited")
    assert ign is not None
    lsf = ce.calculate_lsf(ign["CaO"], ign["SiO2"], ign["Al2O3"], ign["Fe2O3"], basis="ignited")
    assert isinstance(lsf, float)
