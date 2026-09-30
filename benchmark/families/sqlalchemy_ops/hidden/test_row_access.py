import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _db import database  # noqa: E402
from sa_testlib import case, need  # noqa: E402
from sqlalchemy import Column, Integer, MetaData, String, Table, select, text  # noqa: E402

ITEMS = """
CREATE TABLE items (id INTEGER PRIMARY KEY, name VARCHAR(30), qty INTEGER);
INSERT INTO items (id, name, qty) VALUES (1, 'bolt', 40), (2, 'nut', 0), (3, 'washer', NULL);
"""

items = Table("items", MetaData(), Column("id", Integer, primary_key=True), Column("name", String(30)),
              Column("qty", Integer))


@case("fetch_dicts")
def h_dicts_select(mod):
    f = need(mod, "fetch_dicts")
    with database(ITEMS) as (engine, _):
        with engine.connect() as conn:
            out = f(conn, select(items).order_by(items.c.id))
    assert out == [{"id": 1, "name": "bolt", "qty": 40}, {"id": 2, "name": "nut", "qty": 0},
                   {"id": 3, "name": "washer", "qty": None}]
    assert all(type(d) is dict for d in out)


@case("fetch_dicts")
def h_dicts_text(mod):
    f = need(mod, "fetch_dicts")
    with database(ITEMS) as (engine, _):
        with engine.connect() as conn:
            assert f(conn, text("SELECT name AS label, qty * 2 AS doubled FROM items WHERE qty > 0")) == \
                [{"label": "bolt", "doubled": 80}]
            assert f(conn, text("SELECT id FROM items WHERE id > 99")) == []


@case("fetch_column")
def h_column(mod):
    f = need(mod, "fetch_column")
    with database(ITEMS) as (engine, _):
        with engine.connect() as conn:
            assert f(conn, select(items).order_by(items.c.id), "name") == ["bolt", "nut", "washer"]
            assert f(conn, text("SELECT id, qty AS stock FROM items ORDER BY id"), "stock") == [40, 0, None]


@case("fetch_tuples")
def h_tuples(mod):
    f = need(mod, "fetch_tuples")
    with database(ITEMS) as (engine, _):
        with engine.connect() as conn:
            out = f(conn, select(items.c.name, items.c.qty).order_by(items.c.id.desc()))
    assert out == [("washer", None), ("nut", 0), ("bolt", 40)]
    assert all(type(r) is tuple for r in out)


@case("row_has_column")
def h_has_column(mod):
    f = need(mod, "row_has_column")
    with database(ITEMS) as (engine, _):
        with engine.connect() as conn:
            row = conn.execute(select(items).where(items.c.id == 1)).first()
            assert f(row, "name") and f(row, "qty")
            assert not f(row, "price")


@case("row_has_column")
def h_has_column_not_values(mod):
    f = need(mod, "row_has_column")
    with database(ITEMS) as (engine, _):
        with engine.connect() as conn:
            row = conn.execute(text("SELECT 'name' AS label, 5 AS n")).first()
            assert f(row, "label") and f(row, "n")
            assert not f(row, "name"), "a value equal to the name is not a column"


@case("result_keys")
def h_keys(mod):
    f = need(mod, "result_keys")
    with database(ITEMS) as (engine, _):
        with engine.connect() as conn:
            assert f(conn, select(items)) == ["id", "name", "qty"]
            assert f(conn, text("SELECT qty AS stock, name FROM items WHERE id > 99")) == ["stock", "name"]
