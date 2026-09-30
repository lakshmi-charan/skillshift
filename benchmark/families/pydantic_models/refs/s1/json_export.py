"""Invoice models and JSON export for the billing API."""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, field_serializer


def _utc_z(dt):
    # the billing API expects UTC timestamps with second precision and a trailing Z
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class Line(BaseModel):
    sku: str
    quantity: int
    unit_price: Decimal


class Invoice(BaseModel):
    number: str
    issued_at: datetime
    lines: List[Line]
    notes: Optional[str] = None

    @field_serializer("issued_at", when_used="json")
    def _issued_at_utc_z(self, value):
        return _utc_z(value)


def invoice_to_json(invoice):
    """JSON text for the billing API; fields that are None are left out."""
    return invoice.model_dump_json(exclude_none=True)


def invoice_to_pretty_json(invoice):
    """Human-readable JSON (2-space indentation) for the audit log; None fields are left out."""
    return invoice.model_dump_json(exclude_none=True, indent=2)


def invoice_from_json(text):
    """Parse and validate invoice JSON text. Raises ValueError (ValidationError) if invalid."""
    return Invoice.parse_raw(text)


def invoice_total(invoice):
    """Exact total of the invoice lines as a Decimal."""
    return sum((line.quantity * line.unit_price for line in invoice.lines), Decimal("0"))
