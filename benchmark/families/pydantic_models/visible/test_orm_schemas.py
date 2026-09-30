from types import SimpleNamespace

from sa_testlib import case, need


@case("from_orm_object")
def test_from_orm(mod):
    u = need(mod, "user_from_orm")(SimpleNamespace(id=1, name="Ann", email="a@x"))
    assert u.dict() == {"id": 1, "name": "Ann", "email": "a@x"}


@case("from_orm_list")
def test_orders(mod):
    ann = SimpleNamespace(id=1, name="Ann", email="a@x")
    out = need(mod, "orders_from_orm")([SimpleNamespace(id=5, customer=ann, items=[])])
    assert out[0].customer.name == "Ann"


@case("required_fields")
def test_required(mod):
    assert need(mod, "required_fields")(mod.OrderSchema) == ["id", "customer"]
    assert mod.OrderSchema.__fields__["items"].required is False
