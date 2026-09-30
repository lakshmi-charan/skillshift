import pandas as pd

from sa_testlib import case, need


def _base():
    return pd.DataFrame({"date": ["2023-01-02", "2023-01-05"], "account": ["cash", "bank"],
                         "amount": [100.0, -40.0], "memo": ["opening", "fee"]})


@case("add_entry")
def h_add_to_existing(mod):
    f = need(mod, "add_entry")
    base = _base()
    out = f(base, "2023-01-09", "cash", 25.5, "sale")
    assert len(out) == 3 and len(base) == 2, "input must not be modified"
    last = out.iloc[-1]
    assert last["date"] == "2023-01-09" and last["account"] == "cash" and float(last["amount"]) == 25.5
    assert last["memo"] == "sale"
    assert list(out.index) == [0, 1, 2]


@case("add_entry")
def h_add_to_empty(mod):
    out = need(mod, "add_entry")(need(mod, "new_ledger")(), "2023-02-01", "bank", 10)
    assert len(out) == 1 and float(out["amount"].iloc[0]) == 10.0 and out["memo"].iloc[0] == ""
    assert list(out.columns)[:4] == ["date", "account", "amount", "memo"]


@case("add_entry")
def h_chain(mod):
    f = need(mod, "add_entry")
    led = need(mod, "new_ledger")()
    for i in range(4):
        led = f(led, "2023-03-0%d" % (i + 1), "cash", i)
    assert [float(v) for v in led["amount"]] == [0.0, 1.0, 2.0, 3.0]
    assert list(led.index) == [0, 1, 2, 3]


@case("add_entries")
def h_many(mod):
    f = need(mod, "add_entries")
    base = _base()
    out = f(base, [{"date": "2023-01-10", "account": "bank", "amount": 5.0, "memo": "a"},
                   {"date": "2023-01-11", "account": "cash", "amount": 7.0}])
    assert len(out) == 4 and len(base) == 2
    assert [float(v) for v in out["amount"]] == [100.0, -40.0, 5.0, 7.0]
    assert out["account"].tolist() == ["cash", "bank", "bank", "cash"]
    assert list(out.index) == [0, 1, 2, 3]


@case("add_entries")
def h_many_empty_list(mod):
    out = need(mod, "add_entries")(_base(), [])
    assert len(out) == 2 and [float(v) for v in out["amount"]] == [100.0, -40.0]


@case("add_entries")
def h_many_into_new(mod):
    out = need(mod, "add_entries")(need(mod, "new_ledger")(),
                                   [{"date": "2023-05-01", "account": "cash", "amount": 1.5, "memo": ""}] * 3)
    assert len(out) == 3 and sum(float(v) for v in out["amount"]) == 4.5


@case("balance")
def h_balance(mod):
    f = need(mod, "balance")
    assert f(_base()) == 60.0
    assert f(_base(), "cash") == 100.0 and f(_base(), "bank") == -40.0


@case("balance")
def h_balance_empty(mod):
    f = need(mod, "balance")
    assert f(_base(), "nope") == 0.0
    assert f(need(mod, "new_ledger")()) == 0.0


@case("running_balance")
def h_running(mod):
    f = need(mod, "running_balance")
    df = _base()
    df.loc[2] = ["2023-01-06", "cash", 15.0, "x"]
    assert f(df) == [100.0, 60.0, 75.0]


@case("running_balance")
def h_running_empty(mod):
    assert need(mod, "running_balance")(need(mod, "new_ledger")()) == []
