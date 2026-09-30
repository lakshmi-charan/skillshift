from sa_testlib import case, need


@case("compare")
def test_minor_numeric(mod):
    assert need(mod, "compare_versions")("1.10", "1.9") == 1


@case("sort")
def test_sort(mod):
    assert need(mod, "sort_versions")(["2.0", "10.1", "9.3"]) == ["2.0", "9.3", "10.1"]


@case("minimum")
def test_minimum(mod):
    assert need(mod, "meets_minimum")("3.11.0", "3.8")
