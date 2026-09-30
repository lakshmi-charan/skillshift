from sa_testlib import case, need


@case("functional")
def t_basic(mod):
    f = need(mod, "latency_summary")
    data = [float(v) for v in range(1, 101)]  # 1..100
    out = f(data + [None, None])
    assert out["count"] == 100 and abs(out["mean"] - 50.5) < 1e-9
    # positions 49.5 -> 50 (round half to even), 89.1 -> 90, 98.01 -> 99 (0-based): values 51, 90, 99
    assert (out["p50"], out["p90"], out["p99"]) == (51.0, 90.0, 99.0)


@case("functional")
def t_small(mod):
    out = need(mod, "latency_summary")([30, None, 10, 20])
    assert out["count"] == 3 and out["mean"] == 20.0
    assert (out["p50"], out["p90"], out["p99"]) == (20.0, 30.0, 30.0)
    assert all(isinstance(out[k], float) for k in ("mean", "p50", "p90", "p99")) and isinstance(out["count"], int)


@case("functional")
def t_empty(mod):
    f = need(mod, "latency_summary")
    for bad in ([], [None]):
        try:
            f(bad)
        except ValueError:
            continue
        raise AssertionError("expected ValueError")
