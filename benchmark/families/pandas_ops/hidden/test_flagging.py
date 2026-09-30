import numpy as np
import pandas as pd

from sa_testlib import case, need


def _df():
    return pd.DataFrame({"sensor": ["a", "b", "c", "d"], "reading": [3.0, 9.5, 12.0, 7.0]})


@case("flag_above")
def h_flag(mod):
    src = _df()
    out = need(mod, "flag_above")(src, "reading", 8.0)
    assert [bool(v) for v in out["flag"]] == [False, True, True, False]
    assert "flag" not in src.columns, "input must not be modified"


@case("flag_above")
def h_flag_custom_col_boundary(mod):
    out = need(mod, "flag_above")(_df(), "reading", 9.5, flag_col="hot")
    assert [bool(v) for v in out["hot"]] == [False, False, True, False]
    assert out["reading"].tolist() == [3.0, 9.5, 12.0, 7.0]


@case("flag_above")
def h_flag_none(mod):
    out = need(mod, "flag_above")(_df(), "reading", 100)
    assert not out["flag"].any() and len(out) == 4


@case("cap_values")
def h_cap(mod):
    src = _df()
    out = need(mod, "cap_values")(src, "reading", 8.0)
    assert out["reading"].tolist() == [3.0, 8.0, 8.0, 7.0]
    assert src["reading"].tolist() == [3.0, 9.5, 12.0, 7.0], "input must not be modified"


@case("cap_values")
def h_cap_int(mod):
    df = pd.DataFrame({"n": [1, 50, 200]})
    assert need(mod, "cap_values")(df, "n", 100)["n"].tolist() == [1, 50, 100]


@case("cap_values")
def h_cap_other_cols(mod):
    out = need(mod, "cap_values")(_df(), "reading", 0.0)
    assert out["reading"].tolist() == [0.0] * 4 and out["sensor"].tolist() == ["a", "b", "c", "d"]


@case("mark_missing")
def h_missing(mod):
    df = pd.DataFrame({"v": [1.0, np.nan, 3.0], "w": ["x", None, "z"]})
    out = need(mod, "mark_missing")(df, "v")
    assert [bool(x) for x in out["missing"]] == [False, True, False]
    out2 = need(mod, "mark_missing")(df, "w", marker_col="w_missing")
    assert [bool(x) for x in out2["w_missing"]] == [False, True, False] and "w_missing" not in df


@case("flag_count")
def h_count(mod):
    df = pd.DataFrame({"flag": [True, False, True], "hot": [False, False, False]})
    f = need(mod, "flag_count")
    assert f(df) == 2 and f(df, "hot") == 0 and isinstance(f(df), int)
