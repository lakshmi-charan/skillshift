import numpy as np

from sa_testlib import case, need


@case("percentile_report")
def test_report(mod):
    out = need(mod, "percentile_report")([1, 2, 3, 4, 5], qs=(50,))
    assert out == {50: 3.0}


@case("lower_median")
def test_lower(mod):
    a = [1, 2, 3, 4]
    assert need(mod, "lower_median")(a) == np.quantile(a, 0.5, interpolation="lower") == 2.0


@case("iqr")
def test_iqr(mod):
    assert need(mod, "iqr")([1, 2, 3, 4, 5]) == 2.0
