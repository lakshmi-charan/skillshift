from sa_testlib import case, need


@case("stock_and_tags")
def test_tags(mod):
    assert need(mod, "make_item")(sku="S", name="N", price="1.00", tags="A,B").tags == ["a", "b"]


@case("immutable")
def test_immutable(mod):
    item = need(mod, "make_item")(sku="S", name="N", price="1.00")
    try:
        item.stock = 3
    except TypeError:
        return
    raise AssertionError("expected TypeError")


@case("invalid_returns_none")
def test_invalid(mod):
    assert need(mod, "try_parse_item")({"sku": "S", "name": "N", "price": "-1"}) is None
