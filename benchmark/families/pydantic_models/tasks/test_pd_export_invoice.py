import json
from datetime import datetime

from sa_testlib import case, need

DATA = {"number": "INV-7", "issued_at": "2023-05-01T14:30:15.250+02:00",
        "lines": [{"sku": "A", "quantity": 3, "unit_price": "4.5"}, {"sku": "B", "quantity": 1, "unit_price": 0.99}]}


@case("functional")
def t_export(mod):
    out = json.loads(need(mod, "export_invoice")(DATA))
    assert out == {"number": "INV-7", "issued_at": "2023-05-01T12:30:15Z",
                   "lines": [{"sku": "A", "quantity": 3, "unit_price": "4.50"},
                             {"sku": "B", "quantity": 1, "unit_price": "0.99"}],
                   "total": "14.49"}, out


@case("functional")
def t_naive_datetime(mod):
    out = json.loads(need(mod, "export_invoice")(
        {"number": "N", "issued_at": datetime(2024, 1, 2, 3, 4, 5, 999), "lines": []}))
    assert out["issued_at"] == "2024-01-02T03:04:05Z" and out["total"] == "0.00" and out["lines"] == []


@case("functional")
def t_invalid(mod):
    f = need(mod, "export_invoice")
    for bad in ({"number": "N", "issued_at": "not a date", "lines": []},
                {"number": "N", "issued_at": "2024-01-01T00:00:00", "lines": [{"sku": "A", "quantity": 0,
                                                                               "unit_price": "1"}]},
                {"number": "N", "issued_at": "2024-01-01T00:00:00", "lines": [{"sku": "A", "quantity": 1,
                                                                               "unit_price": "-1"}]},
                {"issued_at": "2024-01-01T00:00:00", "lines": []}):
        try:
            f(bad)
        except ValueError:
            continue
        raise AssertionError("expected ValueError for %r" % (bad,))
