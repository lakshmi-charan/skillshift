import pandas as pd

from sa_testlib import case, need


def _sales():
    return pd.DataFrame({
        "region": ["north", "south", "north", "east", "south", "north"],
        "rep": ["ann", "bo", "cid", "dee", "eve", "fay"],
        "units": [10, 4, 6, 8, 2, 1],
        "revenue": [100.0, 40.0, 66.0, 80.0, 30.0, 12.0],
    })


@case("group_totals")
def h_totals(mod):
    out = need(mod, "group_totals")(_sales(), "region", "revenue")
    assert out == {"east": 80.0, "north": 178.0, "south": 70.0}


@case("group_totals")
def h_totals_int(mod):
    assert need(mod, "group_totals")(_sales(), "region", "units") == {"east": 8, "north": 17, "south": 6}


@case("group_means")
def h_means_ignores_text(mod):
    out = need(mod, "group_means")(_sales(), "region")
    assert sorted(out.columns) == ["revenue", "units"]
    assert abs(out.loc["north", "units"] - 17 / 3) < 1e-12 and out.loc["south", "revenue"] == 35.0


@case("group_means")
def h_means_numeric_only_frame(mod):
    df = pd.DataFrame({"k": ["a", "a", "b"], "x": [1.0, 3.0, 5.0]})
    out = need(mod, "group_means")(df, "k")
    assert out["x"].to_dict() == {"a": 2.0, "b": 5.0}


@case("group_means")
def h_means_two_text_cols(mod):
    df = pd.DataFrame({"k": ["a", "b"], "note": ["x", "y"], "tag": ["p", "q"], "v": [2, 4]})
    out = need(mod, "group_means")(df, "k")
    assert list(out.columns) == ["v"] and out["v"].tolist() == [2.0, 4.0]


@case("top_n_per_group")
def h_top(mod):
    out = need(mod, "top_n_per_group")(_sales(), "region", "revenue", 2)
    assert sorted(out["rep"]) == ["ann", "bo", "cid", "dee", "eve"]
    assert out["revenue"].tolist() == sorted(out["revenue"], reverse=True)


@case("top_n_per_group")
def h_top_one(mod):
    out = need(mod, "top_n_per_group")(_sales(), "region", "units", 1)
    assert dict(zip(out["region"], out["rep"])) == {"north": "ann", "east": "dee", "south": "bo"}
    assert list(out.index) == [0, 1, 2]


@case("share_of_total")
def h_share(mod):
    out = need(mod, "share_of_total")(_sales(), "region", "revenue")
    assert abs(out.iloc[0] - 100 / 178) < 1e-12 and out.iloc[3] == 1.0
    assert abs(out[_sales()["region"] == "south"].sum() - 1.0) < 1e-12


@case("pivot_summary")
def h_pivot(mod):
    df = pd.DataFrame({"region": ["n", "n", "s"], "q": ["q1", "q2", "q1"], "rev": [1, 2, 3]})
    out = need(mod, "pivot_summary")(df, "region", "q", "rev")
    assert out.loc["n", "q1"] == 1 and out.loc["n", "q2"] == 2 and out.loc["s", "q2"] == 0 and out.loc["s", "q1"] == 3


@case("pivot_summary")
def h_pivot_sums(mod):
    out = need(mod, "pivot_summary")(_sales(), "region", "rep", "units")
    assert int(out.values.sum()) == 31 and out.shape == (3, 6)
