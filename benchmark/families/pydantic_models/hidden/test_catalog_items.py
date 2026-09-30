import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.dirname(__file__))
from _util import raises_value_error  # noqa: E402
from sa_testlib import case, need  # noqa: E402

BASE = {"sku": "MUG-1", "name": "Mug", "price": "4.50"}


def _with(**kw):
    d = dict(BASE)
    d.update(kw)
    return d


@case("name_rules")
def h_name(mod):
    f = need(mod, "make_item")
    assert f(**_with(name="  Blue Mug  ")).name == "Blue Mug"
    assert f(**_with(name="x" * 60)).name == "x" * 60
    assert raises_value_error(f, **_with(name="   "))
    assert raises_value_error(f, **_with(name="x" * 61))


@case("price_rules")
def h_price(mod):
    f = need(mod, "make_item")
    assert f(**BASE).price == Decimal("4.50")
    assert f(**_with(price=12)).price == Decimal("12")
    for bad in ("0", "-1", "4.505", "12345678901"):
        assert raises_value_error(f, **_with(price=bad)), bad


@case("stock_and_tags")
def h_stock(mod):
    f = need(mod, "make_item")
    assert f(**BASE).stock == 0 and f(**_with(stock="7")).stock == 7
    assert raises_value_error(f, **_with(stock=-1))


@case("stock_and_tags")
def h_tags(mod):
    f = need(mod, "make_item")
    assert f(**_with(tags="Kitchen, blue ,, GIFT")).tags == ["kitchen", "blue", "gift"]
    assert f(**_with(tags=["A", " b "])).tags == ["a", "b"]
    assert f(**BASE).tags == []
    assert raises_value_error(f, **_with(tags="a,b,c,d,e,f"))


@case("immutable")
def h_immutable(mod):
    item = need(mod, "make_item")(**BASE)
    for field, value in (("price", Decimal("1.00")), ("stock", 5), ("name", "Other")):
        try:
            setattr(item, field, value)
        except Exception:
            pass
        assert getattr(item, field) != value, "items must be immutable (%s changed)" % field


@case("immutable")
def h_immutable_other_instances(mod):
    f = need(mod, "make_item")
    a, b = f(**BASE), f(**_with(sku="MUG-2"))
    try:
        b.sku = "MUG-1"
    except Exception:
        pass
    assert (a.sku, b.sku) == ("MUG-1", "MUG-2")


@case("invalid_returns_none")
def h_try_valid(mod):
    f = need(mod, "try_parse_item")
    item = f(_with(tags="a,b", stock=3))
    assert item is not None and item.tags == ["a", "b"] and item.stock == 3


@case("invalid_returns_none")
def h_try_invalid(mod):
    f = need(mod, "try_parse_item")
    assert f(_with(price="0")) is None
    assert f({"sku": "X"}) is None
    assert f(_with(tags=None)) is None
    assert f(_with(tags=7)) is None
