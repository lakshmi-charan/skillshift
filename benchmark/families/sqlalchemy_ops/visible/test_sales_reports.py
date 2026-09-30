from sa_testlib import case, need
from sqlalchemy import create_engine, select


def _conn(mod):
    engine = create_engine("sqlite://")
    need(mod, "metadata").create_all(engine)
    conn = engine.connect()
    conn.execute(mod.customers.insert(), [{"id": 1, "name": "Ann", "region": "n"}, {"id": 2, "name": "Bob", "region": "s"}])
    conn.execute(mod.invoices.insert(), [{"customer_id": 1, "amount": 10, "issued_on": "2024-01-01"},
                                         {"customer_id": 2, "amount": 30, "issued_on": "2024-02-01"},
                                         {"customer_id": 1, "amount": 5, "issued_on": "2024-02-03"}])
    return conn


@case("totals_by_customer")
def test_totals(mod):
    assert need(mod, "totals_by_customer")(_conn(mod)) == {"Ann": 15, "Bob": 30}


@case("big_spenders")
def test_big(mod):
    assert need(mod, "big_spenders")(_conn(mod), 20) == [("Bob", 30)]


@case("count_matching")
def test_count(mod):
    conn = _conn(mod)
    assert need(mod, "count_matching")(conn, select([mod.invoices]).where(mod.invoices.c.amount > 6)) == 2


@case("monthly_revenue")
def test_monthly(mod):
    assert need(mod, "monthly_revenue")(_conn(mod)) == [("2024-01", 10), ("2024-02", 35)]
