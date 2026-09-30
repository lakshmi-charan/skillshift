from sa_testlib import case, need


class O:
    def __init__(self, **kw):
        self.__dict__.update(kw)


@case("functional")
def t_payload(mod):
    ann = O(id=1, name="Ann", email="ann@example.com", password_hash="secret")
    orders = [O(id=10, customer=ann, items=[O(sku="A", quantity=2, cost=1)], note="x"),
              O(id=11, customer=ann, items=[])]
    assert need(mod, "orders_payload")(orders) == [
        {"id": 10, "customer": {"id": 1, "name": "Ann", "email": "ann@example.com"},
         "items": [{"sku": "A", "quantity": 2}]},
        {"id": 11, "customer": {"id": 1, "name": "Ann", "email": "ann@example.com"}, "items": []},
    ]


@case("functional")
def t_invalid(mod):
    f = need(mod, "orders_payload")
    ann = O(id=1, name="Ann", email="ann@example.com")
    for bad in ([O(id=1, customer=ann)], [O(id="one", customer=ann, items=[])],
                [O(id=1, customer=O(id=1, name="Ann"), items=[])]):
        try:
            f(bad)
        except ValueError:
            continue
        raise AssertionError("expected ValueError")
