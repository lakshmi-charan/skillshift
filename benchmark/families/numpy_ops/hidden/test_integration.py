import math

from sa_testlib import case, need


def _close(a, b, tol=1e-9):
    return abs(a - b) <= tol * max(1.0, abs(b))


@case("area_under_curve")
def h_auc_x(mod):
    f = need(mod, "area_under_curve")
    assert _close(f([0, 1, 4, 9], x=[0, 1, 2, 3]), 9.5)
    assert _close(f([1, 1], x=[0, 10]), 10.0)


@case("area_under_curve")
def h_auc_dx(mod):
    f = need(mod, "area_under_curve")
    assert _close(f([1, 2, 3]), 4.0)
    assert _close(f([1, 2, 3], dx=0.5), 2.0)
    assert isinstance(f([1, 2]), float)


@case("area_under_curve")
def h_auc_uneven(mod):
    assert _close(need(mod, "area_under_curve")([2, 2, 4], x=[0, 3, 4]), 9.0)


@case("mean_level")
def h_mean_level(mod):
    f = need(mod, "mean_level")
    assert _close(f([0, 10], [0, 2]), 5.0)
    assert _close(f([3, 3, 3], [1, 2, 5]), 3.0)
    assert _close(f([2, 2, 4], [0, 3, 4]), 2.25)


@case("cumulative_area")
def h_cum(mod):
    out = need(mod, "cumulative_area")([0, 1, 4, 9], [0, 1, 2, 3])
    assert all(_close(a, b) for a, b in zip(out, [0.0, 0.5, 3.0, 9.5])) and len(out) == 4


@case("polygon_area")
def h_poly_square(mod):
    f = need(mod, "polygon_area")
    assert _close(f([0, 2, 2, 0], [0, 0, 2, 2]), 4.0)
    assert _close(f([0, 0, 2, 2], [0, 2, 2, 0]), 4.0), "orientation must not matter"


@case("polygon_area")
def h_poly_triangle_concave(mod):
    f = need(mod, "polygon_area")
    assert _close(f([0, 4, 0], [0, 0, 3]), 6.0)
    # L-shape (concave hexagon) of area 3
    assert _close(f([0, 2, 2, 1, 1, 0], [0, 0, 1, 1, 2, 2]), 3.0)


@case("resample_signal")
def h_resample(mod):
    f = need(mod, "resample_signal")
    assert f([0, 10], [0, 100], [2.5, 5, 10]) == [25.0, 50.0, 100.0]
    assert f([0, 1], [1, 3], [-1, 2]) == [1.0, 3.0]
