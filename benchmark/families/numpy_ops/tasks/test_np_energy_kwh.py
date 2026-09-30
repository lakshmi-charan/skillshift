from sa_testlib import case, need


def _close(a, b):
    return abs(a - b) <= 1e-9 * max(1.0, abs(b))


@case("functional")
def t_constant(mod):
    f = need(mod, "energy_kwh")
    out = f([0, 3600], [1000, 1000])
    assert _close(out, 1.0) and isinstance(out, float)


@case("functional")
def t_uneven_ramp(mod):
    f = need(mod, "energy_kwh")
    # 0->2000 W over 1800 s, then flat 2000 W for 900 s: 1.8e6 J + 1.8e6 J = 1.0 kWh
    assert _close(f([0, 1800, 2700], [0, 2000, 2000]), 1.0)


@case("functional")
def t_short(mod):
    f = need(mod, "energy_kwh")
    assert f([], []) == 0.0 and f([5], [100]) == 0.0
