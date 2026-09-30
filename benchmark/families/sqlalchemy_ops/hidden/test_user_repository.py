import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _db import database, rows  # noqa: E402
from sa_testlib import case, need  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

# users 1 (Ann), 2 (Bob); orders 1 -> Bob, 2 -> Ann, 3 -> Bob, 4 -> Ann  (ids overlap on purpose)
SEED = """
INSERT INTO users (id, name, email) VALUES (1, 'Ann', 'ann@example.com'), (2, 'Bob', 'bob@example.com');
INSERT INTO orders (id, user_id, status, total) VALUES
  (1, 2, 'paid', 700), (2, 1, 'new', 500), (3, 2, 'new', 250), (4, 1, 'paid', 300);
"""


class _Repo:
    def __init__(self, mod, seed=True):
        self.mod = mod
        self.cm = database()

    def __enter__(self):
        self.engine, self.path = self.cm.__enter__()
        need(self.mod, "create_schema")(self.engine)
        import sqlite3
        con = sqlite3.connect(self.path)
        con.executescript(SEED)
        con.commit()
        con.close()
        self.session = Session(self.engine)
        return self

    def __exit__(self, *a):
        self.session.close()
        return self.cm.__exit__(*a)


@case("add_records")
def h_add_user(mod):
    with _Repo(mod) as r:
        uid = need(mod, "add_user")(r.session, "Cy", "Cy@Example.COM")
        assert isinstance(uid, int) and uid not in (1, 2)
        assert rows(r.path, "SELECT name, email FROM users WHERE id = ?", (uid,)) == [("Cy", "cy@example.com")]


@case("add_records")
def h_add_order(mod):
    with _Repo(mod) as r:
        oid = need(mod, "add_order")(r.session, 1, 999, status="paid")
        oid2 = need(mod, "add_order")(r.session, 2, 10)
        assert rows(r.path, "SELECT user_id, status, total FROM orders WHERE id IN (?, ?) ORDER BY id",
                    (oid, oid2)) == [(1, "paid", 999), (2, "new", 10)]


@case("find_by_email")
def h_find(mod):
    with _Repo(mod) as r:
        f = need(mod, "find_by_email")
        u = f(r.session, "BOB@example.com")
        assert u is not None and u.id == 2 and u.name == "Bob"
        assert f(r.session, "nobody@example.com") is None


@case("get_by_id")
def h_get(mod):
    with _Repo(mod) as r:
        f = need(mod, "get_user")
        assert f(r.session, 1).email == "ann@example.com"
        assert f(r.session, 2).name == "Bob"
        assert f(r.session, 42) is None


@case("orders_for")
def h_orders_for(mod):
    with _Repo(mod) as r:
        f = need(mod, "orders_for")
        assert [o.id for o in f(r.session, "ann@example.com")] == [2, 4]
        assert [o.id for o in f(r.session, "Bob@Example.com")] == [1, 3]


@case("orders_for")
def h_orders_for_status(mod):
    with _Repo(mod) as r:
        f = need(mod, "orders_for")
        assert [(o.id, o.total) for o in f(r.session, "bob@example.com", status="new")] == [(3, 250)]
        assert f(r.session, "ann@example.com", status="cancelled") == []
        assert f(r.session, "ghost@example.com") == []


@case("owner_of_order")
def h_owner(mod):
    with _Repo(mod) as r:
        f = need(mod, "owner_of_order")
        assert f(r.session, 1).name == "Bob"
        assert f(r.session, 2).name == "Ann"
        assert f(r.session, 3).name == "Bob"


@case("owner_of_order")
def h_owner_missing(mod):
    with _Repo(mod) as r:
        f = need(mod, "owner_of_order")
        assert f(r.session, 99) is None
        assert f(r.session, 4).email == "ann@example.com"
