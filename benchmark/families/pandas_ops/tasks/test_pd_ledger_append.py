import pandas as pd

from sa_testlib import case, need


def _ledger():
    return pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "account": ["cash", "bank"], "amount": [50.0, -20.0]})


@case("functional")
def t_append(mod):
    f = need(mod, "append_transactions")
    src = _ledger()
    out = f(src, [{"date": "2023-01-03", "account": "cash", "amount": 5.0},
                  {"date": "2023-01-04", "account": "bank", "amount": -1.5}])
    assert list(out.index) == [0, 1, 2, 3]
    assert [float(v) for v in out["amount"]] == [50.0, -20.0, 5.0, -1.5]
    assert [float(v) for v in out["balance"]] == [50.0, 30.0, 35.0, 33.5]
    assert out["account"].tolist() == ["cash", "bank", "cash", "bank"]
    assert len(src) == 2 and "balance" not in src.columns


@case("functional")
def t_empty_ledger(mod):
    f = need(mod, "append_transactions")
    empty = pd.DataFrame(columns=["date", "account", "amount"])
    out = f(empty, [{"date": "2023-02-01", "account": "cash", "amount": 3}])
    assert len(out) == 1 and float(out["balance"].iloc[0]) == 3.0


@case("functional")
def t_existing_balance_recomputed(mod):
    f = need(mod, "append_transactions")
    led = _ledger()
    led["balance"] = [0.0, 0.0]
    out = f(led, [])
    assert [float(v) for v in out["balance"]] == [50.0, 30.0] and len(out) == 2
