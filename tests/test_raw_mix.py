import math
import pandas as pd
from src.chemistry import raw_mix as rm


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


def test_rm001_rm002_calculations():
    df = _build_materials_df()

    # RM001 proportions (percents that sum to 100)
    mix_rm001 = {"MAT005": 86.5, "MAT011": 10.0, "MAT009": 1.5, "MAT010": 2.0}
    raw1 = rm.compute_weighted_oxides(df, mix_rm001)

    # Check raw oxide sums roughly match provided notes
    assert almost_equal(raw1["CaO"], 37.95, tol=0.05)
    assert almost_equal(raw1["SiO2"], 9.98, tol=0.05)
    assert almost_equal(raw1["Al2O3"], 3.01, tol=0.05)
    assert almost_equal(raw1["Fe2O3"], 2.64, tol=0.05)
    assert almost_equal(raw1["MgO"], 3.67, tol=0.05)
    assert almost_equal(raw1["LOI"], 39.45, tol=0.1)

    ign1, mult1 = rm.ignited_basis(raw1)
    assert almost_equal(ign1["CaO"], 62.67, tol=0.05)
    assert almost_equal(ign1["SiO2"], 16.48, tol=0.05)

    mods1 = rm.compute_moduli(ign1)
    assert almost_equal(mods1["LSF"], 114.3, tol=0.3)
    assert almost_equal(mods1["SM"], 1.77, tol=0.02)
    assert almost_equal(mods1["AM"], 1.14, tol=0.02)

    # RM002
    mix_rm002 = {"MAT006": 82.0, "MAT007": 12.0, "MAT008": 5.0, "MAT009": 1.0}
    raw2 = rm.compute_weighted_oxides(df, mix_rm002)
    assert almost_equal(raw2["CaO"], 36.44, tol=0.05)
    assert almost_equal(raw2["SiO2"], 20.31, tol=0.05)
    assert almost_equal(raw2["Al2O3"], 5.27, tol=0.05)
    assert almost_equal(raw2["LOI"], 31.33, tol=0.1)

    ign2, mult2 = rm.ignited_basis(raw2)
    assert almost_equal(ign2["CaO"], 53.06, tol=0.06)
    assert almost_equal(ign2["SiO2"], 29.57, tol=0.06)

    mods2 = rm.compute_moduli(ign2)
    assert almost_equal(mods2["LSF"], 56.0, tol=0.5)
    assert almost_equal(mods2["SM"], 2.47, tol=0.03)
    assert almost_equal(mods2["AM"], 1.79, tol=0.03)


if __name__ == "__main__":
    test_rm001_rm002_calculations()
    print("raw mix tests passed")
