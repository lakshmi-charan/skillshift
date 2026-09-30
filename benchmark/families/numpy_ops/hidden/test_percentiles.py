from sa_testlib import case, need

DATA = [7, 1, 3, 9, 5, 11, 13, 15, 17, 19]


def _close(a, b, tol=1e-9):
    return abs(a - b) <= tol * max(1.0, abs(b))


@case("percentile_report")
def h_report_default(mod):
    out = need(mod, "percentile_report")(DATA)
    assert list(out) == [5, 25, 50, 75, 95]
    exp = {5: 1.9, 25: 5.5, 50: 10.0, 75: 14.5, 95: 18.1}
    assert all(_close(out[q], exp[q]) for q in exp)


@case("percentile_report")
def h_report_custom(mod):
    out = need(mod, "percentile_report")([10, 20, 30, 40], qs=(0, 50, 100, 10))
    exp = {0: 10.0, 50: 25.0, 100: 40.0, 10: 13.0}
    assert list(out) == [0, 50, 100, 10] and all(_close(out[q], exp[q]) for q in exp)


@case("lower_median")
def h_lower_median_even(mod):
    f = need(mod, "lower_median")
    assert f([4, 1, 3, 2]) == 2.0 and f(DATA) == 9.0


@case("lower_median")
def h_lower_median_odd(mod):
    f = need(mod, "lower_median")
    assert f([5, 1, 3]) == 3.0 and f([2.5]) == 2.5


@case("iqr")
def h_iqr(mod):
    assert _close(need(mod, "iqr")(DATA), 9.0)
    assert need(mod, "iqr")([1, 1, 1]) == 0.0


@case("clip_to_percentiles")
def h_clip(mod):
    out = need(mod, "clip_to_percentiles")(list(range(101)), lo=10, hi=90)
    assert out[0] == 10.0 and out[-1] == 90.0 and out[50] == 50.0 and len(out) == 101


@case("clip_to_percentiles")
def h_clip_default(mod):
    out = need(mod, "clip_to_percentiles")([0] * 50 + [1000] + [1] * 49)
    assert max(out) < 1000 and min(out) == 0.0
