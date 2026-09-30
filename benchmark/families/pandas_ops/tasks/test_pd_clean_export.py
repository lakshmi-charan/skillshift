import pandas as pd

from sa_testlib import case, need

CSV = "Customer Name, Unit Price ($),Qty\n  Ada  ,1.50,2\n,,\nBob ,2.25,1\n Cy,3.00,\n"


@case("functional")
def t_clean(mod):
    out = need(mod, "clean_export")(CSV)
    assert list(out.columns) == ["customer_name", "unit_price", "qty"]
    assert out["customer_name"].tolist() == ["Ada", "Bob", "Cy"]
    assert list(out.index) == [0, 1, 2]


@case("functional")
def t_numeric(mod):
    out = need(mod, "clean_export")(CSV)
    assert out["unit_price"].tolist() == [1.5, 2.25, 3.0]
    assert pd.api.types.is_numeric_dtype(out["qty"]) and pd.isna(out["qty"].iloc[2])


@case("functional")
def t_inner_spaces_kept(mod):
    out = need(mod, "clean_export")("City\n  New York \n")
    assert out["city"].tolist() == ["New York"]
