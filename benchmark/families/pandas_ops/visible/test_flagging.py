import pandas as pd

from sa_testlib import case, need


@case("flag_above")
def test_flag(mod):
    out = need(mod, "flag_above")(pd.DataFrame({"v": [1, 5, 10]}), "v", 4)
    assert out["flag"].tolist() == [False, True, True]


@case("cap_values")
def test_cap(mod):
    assert need(mod, "cap_values")(pd.DataFrame({"v": [1, 5, 10]}), "v", 4)["v"].tolist() == [1, 4, 4]


@case("flag_count")
def test_count(mod):
    assert need(mod, "flag_count")(pd.DataFrame({"flag": [True, True, False]})) == 2
