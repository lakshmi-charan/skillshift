from collections import OrderedDict
from decimal import Decimal

from sa_testlib import case, need

ORDER = {"id": 1, "customer": "ACME", "items": [{"sku": "A", "quantity": 2, "unit_price": Decimal("1.50")}]}


@case("context_totals")
def test_totals(mod):
    out = need(mod, "dump_order")(ORDER, tax_rate="0.1")
    assert out["total"] == "3.30"
    assert isinstance(out, OrderedDict)


@case("load_validation")
def test_load(mod):
    out = need(mod, "load_order")({"id": 1, "customer": "ACME", "items": [{"sku": "A", "quantity": 1, "unit_price": "2.00"}]})
    assert out["items"][0]["unit_price"] == Decimal("2.00")
