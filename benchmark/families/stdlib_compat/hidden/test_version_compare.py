from sa_testlib import case, need


@case("compare")
def h_compare_numeric(mod):
    f = need(mod, "compare_versions")
    assert f("1.10", "1.9") == 1
    assert f("1.9", "1.10") == -1
    assert f("0.9.12", "0.10.0") == -1
    assert f("10.0", "9.99") == 1


@case("compare")
def h_compare_equal_and_longer(mod):
    f = need(mod, "compare_versions")
    assert f("2.0.3", "2.0.3") == 0
    assert f("1.2", "1.2.1") == -1
    assert f("3.2.1", "3.2") == 1


@case("sort")
def h_sort(mod):
    f = need(mod, "sort_versions")
    vs = ["1.10", "1.2", "1.9", "1.10.1", "0.99", "1.2.10", "1.2.9"]
    assert f(vs) == ["0.99", "1.2", "1.2.9", "1.2.10", "1.9", "1.10", "1.10.1"]
    assert f(vs, reverse=True) == ["1.10.1", "1.10", "1.9", "1.2.10", "1.2.9", "1.2", "0.99"]
    assert vs[0] == "1.10", "input list must not be modified"


@case("latest")
def h_latest(mod):
    f = need(mod, "latest_version")
    assert f(["3.9.1", "3.10.0", "3.9.10"]) == "3.10.0"
    assert f(iter(["0.1", "0.10", "0.9"])) == "0.10"


@case("latest")
def h_latest_empty(mod):
    assert need(mod, "latest_version")([]) is None


@case("minimum")
def h_minimum(mod):
    f = need(mod, "meets_minimum")
    assert f("3.10.2", "3.9") is True
    assert f("1.2", "1.10") is False
    assert f("2.4.1", "2.4.1") is True
    assert f("21.0", "21.0.1") is False
