from decimal import Decimal

from sa_testlib import case, need

ORDER_IN = {"id": 17, "customer": "ACME", "items": [
    {"sku": "BOLT", "quantity": 10, "unit_price": "0.25"},
    {"sku": "NUT", "quantity": 3, "unit_price": "1.10"}]}


def _order():
    return {"id": 17, "customer": "ACME", "items": [
        {"sku": "BOLT", "quantity": 10, "unit_price": Decimal("0.25")},
        {"sku": "NUT", "quantity": 3, "unit_price": Decimal("1.10")}]}


@case("load_validation")
def h_load(mod):
    f = need(mod, "load_order")
    out = f(ORDER_IN)
    assert out["id"] == 17 and out["customer"] == "ACME"
    assert out["items"][1] == {"sku": "NUT", "quantity": 3, "unit_price": Decimal("1.10")}


@case("load_validation")
def h_load_invalid(mod):
    from marshmallow import ValidationError
    f = need(mod, "load_order")
    bad = {"id": 1, "customer": "X", "items": [{"sku": "A", "quantity": 0, "unit_price": "1"}]}
    try:
        f(bad)
    except ValidationError as e:
        assert "items" in e.messages
    else:
        raise AssertionError("quantity 0 accepted")
    try:
        f({"id": 1, "items": []})
    except ValidationError as e:
        assert "customer" in e.messages
    else:
        raise AssertionError("missing customer accepted")


@case("dump_items")
def h_items(mod):
    f = need(mod, "dump_items")
    out = f([{"sku": "A", "quantity": 2, "unit_price": Decimal("19.9")}])
    assert out == [{"sku": "A", "quantity": 2, "unit_price": "19.90"}]
    assert list(out[0]) == ["sku", "quantity", "unit_price"]


@case("context_totals")
def h_totals_default(mod):
    f = need(mod, "dump_order")
    out = f(_order())
    assert (out["subtotal"], out["tax"], out["total"], out["currency"]) == ("5.80", "0.00", "5.80", "USD")
    assert list(out) == ["id", "customer", "items", "subtotal", "tax", "total", "currency"]


@case("context_totals")
def h_totals_tax(mod):
    f = need(mod, "dump_order")
    out = f(_order(), tax_rate="0.2", currency="EUR")
    assert (out["subtotal"], out["tax"], out["total"], out["currency"]) == ("5.80", "1.16", "6.96", "EUR")
    out2 = f(_order(), tax_rate=0.075)
    assert (out2["tax"], out2["total"]) == ("0.44", "6.24")


@case("summary")
def h_summary(mod):
    f = need(mod, "order_summary")
    o2 = _order()
    o2["id"] = 18
    o2["items"] = [{"sku": "X", "quantity": 1, "unit_price": Decimal("10.00")}]
    out = f([_order(), o2], tax_rate="0.1", currency="GBP")
    assert out["count"] == 2 and [o["id"] for o in out["orders"]] == [17, 18]
    assert out["grand_total"] == "17.38"
    assert all(o["currency"] == "GBP" for o in out["orders"])


@case("summary")
def h_summary_empty(mod):
    assert need(mod, "order_summary")([]) == {"orders": [], "count": 0, "grand_total": "0.00"}
