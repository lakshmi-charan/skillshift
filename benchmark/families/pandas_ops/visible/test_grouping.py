import pandas as pd

from sa_testlib import case, need

DF = pd.DataFrame({"k": ["a", "a", "b"], "name": ["x", "y", "z"], "v": [1.0, 3.0, 5.0]})


@case("group_totals")
def test_totals(mod):
    assert need(mod, "group_totals")(DF, "k", "v") == {"a": 4.0, "b": 5.0}


@case("group_means")
def test_means(mod):
    assert need(mod, "group_means")(DF, "k")["v"].tolist() == [2.0, 5.0]


@case("pivot_summary")
def test_pivot(mod):
    out = need(mod, "pivot_summary")(DF, "k", "name", "v")
    assert out.loc["b", "x"] == 0
