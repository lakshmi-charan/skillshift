import numpy as np

from sa_testlib import case, need


@case("keep_allowed")
def test_keep(mod):
    assert need(mod, "keep_allowed")([1, 2, 3, 4], [2, 4]) == [2, 4]


@case("drop_blocked")
def test_drop(mod):
    assert need(mod, "drop_blocked")([1, 2, 3, 4], [2, 4]) == [1, 3]


@case("keep_allowed")
def test_matches_in1d(mod):
    a, b = np.array([3, 1, 2]), np.array([1, 2])
    assert need(mod, "keep_allowed")(a, b) == a[np.in1d(a, b)].tolist()
