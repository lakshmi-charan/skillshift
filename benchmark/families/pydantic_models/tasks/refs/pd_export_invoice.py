import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import List

from pydantic import BaseModel

CENT = Decimal("0.01")


class _Line(BaseModel):
    sku: str
    quantity: int
    unit_price: Decimal


class _Invoice(BaseModel):
    number: str
    issued_at: datetime
    lines: List[_Line]


def export_invoice(data):
    inv = _Invoice(**data)
    for line in inv.lines:
        if line.quantity < 1 or line.unit_price < 0:
            raise ValueError("invalid line")
    ts = inv.issued_at
    if ts.tzinfo is not None:
        ts = ts.astimezone(timezone.utc)
    total = sum((ln.quantity * ln.unit_price for ln in inv.lines), Decimal("0"))
    return json.dumps({
        "number": inv.number,
        "issued_at": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "lines": [{"sku": ln.sku, "quantity": ln.quantity, "unit_price": str(ln.unit_price.quantize(CENT))}
                  for ln in inv.lines],
        "total": str(total.quantize(CENT)),
    })
