import math

from src.chemistry.clinker_chemistry import calculate_am, calculate_lsf, calculate_sm


def test_lsf_calculation():
    value = calculate_lsf(64, 22, 5, 3)
    assert math.isclose(value, 64 / (2.8 * 22 + 1.18 * 5 + 0.65 * 3), rel_tol=1e-6)


def test_sm_calculation():
    value = calculate_sm(22, 5, 3)
    assert math.isclose(value, 22 / (5 + 3), rel_tol=1e-6)


def test_am_calculation():
    value = calculate_am(5, 3)
    assert math.isclose(value, 5 / 3, rel_tol=1e-6)
