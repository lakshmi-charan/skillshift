import numpy as np
import pandas as pd

from sa_testlib import case, need


def _df():
    return pd.DataFrame({
        "name": ["  Ada ", "Bob", None, "Cy  "],
        "city": ["Paris ", " Rome", "Oslo", None],
        "qty": [1, 2, 3, 4],
        "price": [1.5, np.nan, 2.0, 3.25],
    })


@case("strip_whitespace")
def h_strip(mod):
    out = need(mod, "strip_whitespace")(_df())
    assert out["name"].tolist()[:2] == ["Ada", "Bob"] and out["name"].iloc[3] == "Cy"
    assert pd.isna(out["name"].iloc[2]) and pd.isna(out["city"].iloc[3])
    assert out["city"].tolist()[:3] == ["Paris", "Rome", "Oslo"]


@case("strip_whitespace")
def h_strip_numbers_untouched(mod):
    src = _df()
    out = need(mod, "strip_whitespace")(src)
    assert out["qty"].tolist() == [1, 2, 3, 4]
    assert out["price"].iloc[0] == 1.5 and pd.isna(out["price"].iloc[1])
    assert src["name"].iloc[0] == "  Ada ", "input must not be modified"


@case("strip_whitespace")
def h_strip_inner_space(mod):
    out = need(mod, "strip_whitespace")(pd.DataFrame({"a": ["  new  york "]}))
    assert out["a"].iloc[0] == "new  york"


@case("text_columns")
def h_text(mod):
    assert need(mod, "text_columns")(_df()) == ["name", "city"]


@case("text_columns")
def h_text_mixed_types(mod):
    df = pd.DataFrame({"flag": [True, False], "when": pd.to_datetime(["2023-01-01", "2023-01-02"]),
                       "code": ["A1", "B2"], "n": [1.0, 2.0], "label": ["x", None]})
    assert need(mod, "text_columns")(df) == ["code", "label"]


@case("text_columns")
def h_text_none(mod):
    assert need(mod, "text_columns")(pd.DataFrame({"a": [1, 2], "b": [0.5, 1.5]})) == []


@case("null_counts")
def h_nulls(mod):
    assert need(mod, "null_counts")(_df()) == {"name": 1, "city": 1, "qty": 0, "price": 1}


@case("null_counts")
def h_nulls_all_missing(mod):
    df = pd.DataFrame({"a": [np.nan, np.nan], "b": ["x", None]})
    out = need(mod, "null_counts")(df)
    assert out == {"a": 2, "b": 1} and all(isinstance(v, int) for v in out.values())


@case("drop_empty_rows")
def h_drop(mod):
    df = pd.DataFrame({"a": [1.0, np.nan, 3.0, np.nan], "b": ["x", None, None, None]})
    out = need(mod, "drop_empty_rows")(df)
    assert list(out.index) == [0, 1] and out["a"].tolist() == [1.0, 3.0]


@case("drop_empty_rows")
def h_drop_keep_partial(mod):
    df = pd.DataFrame({"a": [np.nan, 2.0], "b": ["y", "z"]})
    assert len(need(mod, "drop_empty_rows")(df)) == 2


@case("normalise_headers")
def h_headers(mod):
    df = pd.DataFrame(columns=[" Order ID", "Unit Price ($)", "qty"])
    assert list(need(mod, "normalise_headers")(df).columns) == ["order_id", "unit_price", "qty"]


@case("normalise_headers")
def h_headers_values_kept(mod):
    df = pd.DataFrame({"First Name": ["a"], "AGE": [3]})
    out = need(mod, "normalise_headers")(df)
    assert list(out.columns) == ["first_name", "age"] and out["age"].tolist() == [3]
