from datetime import datetime
from decimal import Decimal

from sa_testlib import case, need


def _inv(mod):
    return mod.Invoice(number="INV-1", issued_at=datetime(2023, 5, 1, 12, 0),
                       lines=[mod.Line(sku="A", quantity=2, unit_price=Decimal("4.50"))])


@case("json_content")
def test_json(mod):
    assert need(mod, "invoice_to_json")(_inv(mod)) == (
        '{"number": "INV-1", "issued_at": "2023-05-01T12:00:00Z", '
        '"lines": [{"sku": "A", "quantity": 2, "unit_price": 4.5}]}')


@case("invoice_total")
def test_total(mod):
    assert need(mod, "invoice_total")(_inv(mod)) == Decimal("9.00")


@case("from_json")
def test_roundtrip(mod):
    inv = _inv(mod)
    assert need(mod, "invoice_from_json")(need(mod, "invoice_to_json")(inv)).lines == inv.lines
