from sa_testlib import case, need


@case("describe")
def test_describe(mod):
    assert need(mod, "describe")([1, 2, 3])["mean"] == 2.0


@case("geometric_mean")
def test_gmean(mod):
    assert abs(need(mod, "geometric_mean")([1, 4]) - 2.0) < 1e-12


@case("nan_mean")
def test_nanmean(mod):
    assert need(mod, "nan_mean")([1, None, 3]) == 2.0
