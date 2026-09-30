from sa_testlib import case, need


@case("lockout_limit")
def h_limit(mod):
    t = need(mod, "Throttle")()
    for _ in range(99):
        t.record_failure("u1")
    assert not t.is_locked("u1")
    t.record_failure("u1")
    assert t.is_locked("u1")


@case("lockout_limit")
def h_per_account(mod):
    t = need(mod, "Throttle")()
    for _ in range(100):
        t.record_failure("a")
    assert t.is_locked("a") and not t.is_locked("b")


@case("reset_on_success")
def h_reset(mod):
    t = need(mod, "Throttle")()
    for _ in range(60):
        t.record_failure("u")
    t.record_success("u")
    for _ in range(60):
        t.record_failure("u")
    assert not t.is_locked("u")
