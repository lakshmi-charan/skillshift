import pandas as pd

from sa_testlib import case, need


@case("strip_whitespace")
def test_strip(mod):
    out = need(mod, "strip_whitespace")(pd.DataFrame({"a": [" x ", "y "], "n": [1, 2]}))
    assert out["a"].tolist() == ["x", "y"] and out["a"].dtype == object


@case("text_columns")
def test_text(mod):
    assert need(mod, "text_columns")(pd.DataFrame({"a": ["x"], "n": [1]})) == ["a"]


@case("null_counts")
def test_nulls(mod):
    assert need(mod, "null_counts")(pd.DataFrame({"a": [None, "x"], "n": [1, 2]})) == {"a": 1, "n": 0}
