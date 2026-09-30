from sa_testlib import case, need


@case("lockout_limit")
def test_100(mod):
    t = need(mod, "Throttle")()
    for _ in range(100):
        t.record_failure("x")
    assert t.is_locked("x")
