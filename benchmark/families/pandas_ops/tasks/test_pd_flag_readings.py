import pandas as pd

from sa_testlib import case, need


@case("functional")
def t_status(mod):
    f = need(mod, "flag_readings")
    src = pd.DataFrame({"id": [1, 2, 3, 4, 5], "temp": [15.0, 20.0, 25.0, 30.0, 35.0]})
    out = f(src, "temp", 18.0, 30.0)
    assert out["status"].tolist() == ["low", "ok", "ok", "ok", "high"]
    assert "status" not in src.columns and out["temp"].tolist() == src["temp"].tolist()


@case("functional")
def t_all_ok(mod):
    out = need(mod, "flag_readings")(pd.DataFrame({"v": [1, 2]}), "v", 0, 10)
    assert out["status"].tolist() == ["ok", "ok"]


@case("functional")
def t_all_out(mod):
    out = need(mod, "flag_readings")(pd.DataFrame({"v": [-5, 50, -1]}), "v", 0, 10)
    assert out["status"].tolist() == ["low", "high", "low"]
