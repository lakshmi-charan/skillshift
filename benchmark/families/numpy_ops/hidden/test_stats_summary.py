import math

from sa_testlib import case, need


def _close(a, b, tol=1e-9):
    return abs(a - b) <= tol * max(1.0, abs(b))


@case("describe")
def h_describe(mod):
    out = need(mod, "describe")([2, 4, 4, 4, 5, 5, 7, 9])
    assert out == {"count": 8, "mean": 5.0, "std": 2.0, "min": 2.0, "max": 9.0}
    assert all(type(v) in (int, float) for v in out.values())


@case("describe")
def h_describe_empty(mod):
    try:
        need(mod, "describe")([])
    except ValueError:
        return
    raise AssertionError("expected ValueError")


@case("geometric_mean")
def h_gmean(mod):
    f = need(mod, "geometric_mean")
    assert _close(f([1, 4]), 2.0) and _close(f([2, 8, 4]), 4.0) and _close(f([5]), 5.0)
    assert isinstance(f([1, 4]), float)


@case("geometric_mean")
def h_gmean_invalid(mod):
    f = need(mod, "geometric_mean")
    for bad in ([], [1, 0, 3], [2, -1]):
        try:
            f(bad)
        except ValueError:
            continue
        raise AssertionError("expected ValueError for %r" % (bad,))


@case("cumulative_growth")
def h_growth(mod):
    out = need(mod, "cumulative_growth")([0.1, -0.5, 1.0])
    assert len(out) == 3 and all(_close(a, b) for a, b in zip(out, [1.1, 0.55, 1.1]))
    assert all(isinstance(v, float) for v in out)


@case("cumulative_growth")
def h_growth_empty_zero(mod):
    f = need(mod, "cumulative_growth")
    assert f([]) == [] and f([0.0, 0.0]) == [1.0, 1.0]


@case("nan_mean")
def h_nanmean(mod):
    f = need(mod, "nan_mean")
    assert f([1, None, 3]) == 2.0 and f([float("nan"), 4.0, 8.0]) == 6.0 and f([5]) == 5.0


@case("nan_mean")
def h_nanmean_all_missing(mod):
    f = need(mod, "nan_mean")
    assert math.isnan(f([None, None])) and math.isnan(f([]))


@case("zscores")
def h_z(mod):
    out = need(mod, "zscores")([2, 4, 4, 4, 5, 5, 7, 9])
    assert all(_close(a, b) for a, b in zip(out, [-1.5, -0.5, -0.5, -0.5, 0.0, 0.0, 1.0, 2.0]))


@case("zscores")
def h_z_const(mod):
    assert need(mod, "zscores")([3, 3, 3]) == [0.0, 0.0, 0.0]
