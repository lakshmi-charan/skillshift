from sa_testlib import case, need


@case("add_entry")
def test_add_one(mod):
    led = need(mod, "add_entry")(need(mod, "new_ledger")(), "2023-01-01", "cash", 100)
    assert len(led) == 1 and led["account"].iloc[0] == "cash"


@case("add_entries")
def test_add_many(mod):
    led = need(mod, "add_entries")(need(mod, "new_ledger")(), [{"date": "2023-01-01", "account": "cash", "amount": 1},
                                                              {"date": "2023-01-02", "account": "cash", "amount": 2}])
    assert len(led) == 2


@case("balance")
def test_balance(mod):
    led = need(mod, "add_entry")(need(mod, "new_ledger")(), "2023-01-01", "cash", 100)
    led = need(mod, "add_entry")(led, "2023-01-02", "bank", -30)
    assert need(mod, "balance")(led) == 70.0
