import os
import sys
from typing import List, Optional

sys.path.insert(0, os.path.dirname(__file__))
from _util import Obj, raises_value_error  # noqa: E402
from sa_testlib import case, need  # noqa: E402


def _order(i, cust, items):
    return Obj(id=i, customer=cust, items=items, internal_note="not exported")


@case("from_orm_object")
def h_user_orm(mod):
    u = need(mod, "user_from_orm")(Obj(id=3, name="Ann", email="ann@example.com", password_hash="x"))
    assert (u.id, u.name, u.email) == (3, "Ann", "ann@example.com")
    assert not hasattr(u, "password_hash")


@case("from_orm_object")
def h_user_orm_invalid(mod):
    f = need(mod, "user_from_orm")
    assert raises_value_error(f, Obj(id=3, name="Ann"))
    assert raises_value_error(f, Obj(id="x", name="Ann", email="e"))


@case("from_orm_list")
def h_orders_orm(mod):
    ann = Obj(id=1, name="Ann", email="ann@example.com")
    bob = Obj(id=2, name="Bob", email="bob@example.com")
    out = need(mod, "orders_from_orm")([
        _order(10, ann, [Obj(sku="A-1", quantity=2), Obj(sku="B-2", quantity=1)]),
        _order(11, bob, []),
    ])
    assert [o.id for o in out] == [10, 11]
    assert out[0].customer.name == "Ann" and out[1].customer.email == "bob@example.com"
    assert [(i.sku, i.quantity) for i in out[0].items] == [("A-1", 2), ("B-2", 1)]
    assert out[1].items == []


@case("from_orm_list")
def h_orders_orm_generator_and_invalid(mod):
    f = need(mod, "orders_from_orm")
    ann = Obj(id=1, name="Ann", email="ann@example.com")
    out = f(_order(i, ann, [Obj(sku="S", quantity=i)]) for i in range(3))
    assert [o.items[0].quantity for o in out] == [0, 1, 2]
    assert raises_value_error(f, [_order(1, ann, [Obj(sku="S")])])


@case("from_dict")
def h_user_dict(mod):
    f = need(mod, "user_from_dict")
    u = f({"id": "5", "name": "Cy", "email": "cy@example.com"})
    assert (u.id, u.name, u.email) == (5, "Cy", "cy@example.com")
    assert raises_value_error(f, {"id": 5, "name": "Cy"})


@case("field_names")
def h_field_names(mod):
    f = need(mod, "field_names")
    assert f(mod.OrderSchema) == ["id", "customer", "items"]
    assert f(mod.UserSchema) == ["id", "name", "email"]


@case("field_names")
def h_field_names_other_model(mod):
    from pydantic import BaseModel

    class Thing(BaseModel):
        zeta: int
        alpha: str = "a"
        tags: List[str] = []

    assert need(mod, "field_names")(Thing) == ["zeta", "alpha", "tags"]


@case("required_fields")
def h_required(mod):
    f = need(mod, "required_fields")
    assert f(mod.OrderSchema) == ["id", "customer"]
    assert f(mod.UserSchema) == ["id", "name", "email"]


@case("required_fields")
def h_required_other_model(mod):
    from pydantic import BaseModel

    class Thing(BaseModel):
        a: int
        b: str = "x"
        c: Optional[int] = None
        d: List[int]

    assert need(mod, "required_fields")(Thing) == ["a", "d"]
