import numpy as np

from sa_testlib import case, need


@case("area_under_curve")
def test_auc(mod):
    assert need(mod, "area_under_curve")([0, 1, 2], x=[0, 1, 2]) == 2.0


@case("area_under_curve")
def test_auc_matches_trapz(mod):
    y = np.sin(np.linspace(0, np.pi, 50))
    assert abs(need(mod, "area_under_curve")(y, dx=np.pi / 49) - np.trapz(y, dx=np.pi / 49)) < 1e-12


@case("polygon_area")
def test_square(mod):
    assert need(mod, "polygon_area")([0, 1, 1, 0], [0, 0, 1, 1]) == 1.0
