from sa_testlib import case, need


@case("functional")
def t_limit(mod):
    g = need(mod, "LoginGuard")()
    for _ in range(99):
        g.failed("a")
    assert not g.locked("a")
    g.failed("a")
    assert g.locked("a")


@case("functional")
def t_reset(mod):
    g = need(mod, "LoginGuard")()
    for _ in range(80):
        g.failed("a")
    g.succeeded("a")
    for _ in range(80):
        g.failed("a")
    assert not g.locked("a")
