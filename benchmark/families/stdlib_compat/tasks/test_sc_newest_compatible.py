from sa_testlib import case, need


@case("functional")
def t_basic(mod):
    f = need(mod, "newest_compatible")
    assert f(["1.9", "1.10", "1.2.3"], "1.3") == "1.10"
    assert f(["0.9.12", "0.10.0", "0.10.1"], "0.10") == "0.10.1"


@case("functional")
def t_none(mod):
    f = need(mod, "newest_compatible")
    assert f(["1.0", "1.1"], "2.0") is None
    assert f([], "1.0") is None


@case("functional")
def t_equal_minimum(mod):
    f = need(mod, "newest_compatible")
    assert f(["3.2", "3.1.9"], "3.2") == "3.2"
