"""Order loading and invoice-style serialisation (marshmallow 3)."""
from decimal import ROUND_HALF_UP, Decimal

from marshmallow import Schema, fields, validate

CENT = Decimal("0.01")


class LineItemSchema(Schema):
    class Meta:
        ordered = True

    sku = fields.String(required=True)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    unit_price = fields.Decimal(required=True, places=2, as_string=True)


class OrderSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Integer(required=True)
    customer = fields.String(required=True)
    items = fields.Nested(LineItemSchema, many=True, required=True)
    subtotal = fields.Method("get_subtotal", dump_only=True)
    tax = fields.Method("get_tax", dump_only=True)
    total = fields.Method("get_total", dump_only=True)
    currency = fields.Method("get_currency", dump_only=True)

    def _subtotal(self, order):
        return sum((Decimal(str(i["unit_price"])) * i["quantity"] for i in order["items"]), Decimal(0))

    def _tax(self, order):
        rate = Decimal(str(self.context.get("tax_rate", 0)))
        return (self._subtotal(order) * rate).quantize(CENT, rounding=ROUND_HALF_UP)

    def get_subtotal(self, order):
        return str(self._subtotal(order).quantize(CENT))

    def get_tax(self, order):
        return str(self._tax(order))

    def get_total(self, order):
        return str((self._subtotal(order) + self._tax(order)).quantize(CENT))

    def get_currency(self, order):
        return self.context.get("currency", "USD")


def load_order(data):
    """Validate an incoming order dict (raises marshmallow.ValidationError); prices become Decimal."""
    return OrderSchema().load(data)


def dump_items(items):
    """Serialise line items (prices as 2-decimal strings), keys in declaration order."""
    return LineItemSchema(many=True).dump(items)


def dump_order(order, tax_rate=0, currency="USD"):
    """Serialise an order with subtotal, tax (at tax_rate), total and currency."""
    return OrderSchema(context={"tax_rate": tax_rate, "currency": currency}).dump(order)


def order_summary(orders, tax_rate=0, currency="USD"):
    """{"orders": [...serialised...], "count": n, "grand_total": "<sum of totals>"}."""
    dumped = [dump_order(o, tax_rate=tax_rate, currency=currency) for o in orders]
    grand = sum((Decimal(d["total"]) for d in dumped), Decimal(0))
    return {"orders": dumped, "count": len(dumped), "grand_total": str(grand.quantize(CENT))}
