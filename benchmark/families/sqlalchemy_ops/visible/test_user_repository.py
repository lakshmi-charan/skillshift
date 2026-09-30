from sa_testlib import case, need
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def _session(mod):
    engine = create_engine("sqlite://")
    need(mod, "create_schema")(engine)
    return Session(engine)


@case("add_records")
def test_add_and_find(mod):
    s = _session(mod)
    uid = need(mod, "add_user")(s, "Ann", "Ann@Example.com")
    assert need(mod, "find_by_email")(s, "ann@example.com").id == uid
    assert need(mod, "get_user")(s, uid).name == "Ann"


@case("orders_for")
def test_orders(mod):
    s = _session(mod)
    uid = need(mod, "add_user")(s, "Bob", "bob@example.com")
    need(mod, "add_order")(s, uid, 100)
    need(mod, "add_order")(s, uid, 200, status="paid")
    assert [o.total for o in need(mod, "orders_for")(s, "bob@example.com", status="paid")] == [200]


@case("owner_of_order")
def test_owner(mod):
    s = _session(mod)
    uid = need(mod, "add_user")(s, "Cy", "cy@example.com")
    oid = need(mod, "add_order")(s, uid, 5)
    assert need(mod, "owner_of_order")(s, oid).email == "cy@example.com"
