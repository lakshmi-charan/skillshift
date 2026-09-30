import json
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal

sys.path.insert(0, os.path.dirname(__file__))
from _util import raises_value_error  # noqa: E402
from sa_testlib import case, need  # noqa: E402


def _inv(mod, notes=None, when=datetime(2023, 5, 1, 12, 0, 0, 123456)):
    return mod.Invoice(number="INV-1", issued_at=when, notes=notes,
                       lines=[mod.Line(sku="A", quantity=2, unit_price=Decimal("4.50")),
                              mod.Line(sku="B", quantity=1, unit_price=Decimal("0.99"))])


@case("json_content")
def h_content(mod):
    data = json.loads(need(mod, "invoice_to_json")(_inv(mod)))
    assert data["number"] == "INV-1" and "notes" not in data
    assert [(ln["sku"], ln["quantity"]) for ln in data["lines"]] == [("A", 2), ("B", 1)]
    assert [Decimal(str(ln["unit_price"])) for ln in data["lines"]] == [Decimal("4.50"), Decimal("0.99")]


@case("json_content")
def h_content_notes(mod):
    data = json.loads(need(mod, "invoice_to_json")(_inv(mod, notes="net 30")))
    assert data["notes"] == "net 30" and set(data) == {"number", "issued_at", "lines", "notes"}


@case("timestamp_format")
def h_timestamp(mod):
    data = json.loads(need(mod, "invoice_to_json")(_inv(mod)))
    assert data["issued_at"] == "2023-05-01T12:00:00Z", data["issued_at"]


@case("timestamp_format")
def h_timestamp_aware(mod):
    inv = _inv(mod, when=datetime(2024, 2, 29, 23, 59, 59, tzinfo=timezone.utc))
    assert json.loads(need(mod, "invoice_to_json")(inv))["issued_at"] == "2024-02-29T23:59:59Z"


@case("pretty_json")
def h_pretty(mod):
    text = need(mod, "invoice_to_pretty_json")(_inv(mod))
    assert text.startswith('{\n  "number": "INV-1",\n'), text[:40]
    assert '\n  "lines": [\n    {\n      "sku": "A",' in text
    data = json.loads(text)
    assert "notes" not in data and data["lines"][1]["sku"] == "B"


@case("pretty_json")
def h_pretty_notes(mod):
    data = json.loads(need(mod, "invoice_to_pretty_json")(_inv(mod, notes="n")))
    assert data["notes"] == "n"


@case("from_json")
def h_from_json(mod):
    f = need(mod, "invoice_from_json")
    inv = f('{"number": "INV-9", "issued_at": "2023-05-01T12:00:00Z", '
            '"lines": [{"sku": "A", "quantity": "3", "unit_price": "1.25"}]}')
    assert inv.number == "INV-9" and inv.notes is None
    assert inv.issued_at.replace(tzinfo=None) == datetime(2023, 5, 1, 12, 0, 0)
    assert inv.lines[0].quantity == 3 and inv.lines[0].unit_price == Decimal("1.25")


@case("from_json")
def h_from_json_invalid(mod):
    f = need(mod, "invoice_from_json")
    assert raises_value_error(f, "{not json")
    assert raises_value_error(f, '{"number": "X", "issued_at": "2023-05-01T12:00:00Z"}')
    assert raises_value_error(f, '{"number": "X", "issued_at": "yesterday", "lines": []}')


@case("invoice_total")
def h_total(mod):
    t = need(mod, "invoice_total")(_inv(mod))
    assert t == Decimal("9.99") and isinstance(t, Decimal)
    empty = mod.Invoice(number="E", issued_at=datetime(2023, 1, 1), lines=[])
    assert need(mod, "invoice_total")(empty) == 0
