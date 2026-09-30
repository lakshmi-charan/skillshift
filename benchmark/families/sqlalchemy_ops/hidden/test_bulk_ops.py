import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _db import database, rows  # noqa: E402
from sa_testlib import case, need  # noqa: E402
from sqlalchemy import Column, Integer, MetaData, String, Table  # noqa: E402

EVENTS_DDL = "CREATE TABLE events (id INTEGER PRIMARY KEY, kind VARCHAR(20), actor VARCHAR(20));"
SEED = EVENTS_DDL + """
INSERT INTO events (kind, actor) VALUES ('click', 'ann'), ('view', 'ann'), ('click', 'bob'), ('view', 'cy');
"""


def _events():
    md = MetaData()
    t = Table("events", md, Column("id", Integer, primary_key=True), Column("kind", String(20)),
              Column("actor", String(20)))
    return md, t


@case("ensure_tables")
def h_create(mod):
    f = need(mod, "ensure_tables")
    md, _ = _events()
    Table("audit", md, Column("id", Integer, primary_key=True), Column("note", String(50)))
    with database("CREATE TABLE legacy (x INTEGER);") as (engine, path):
        assert f(engine, md) == ["audit", "events", "legacy"]
        names = {r[0] for r in rows(path, "SELECT name FROM sqlite_master WHERE type='table'")}
        assert {"audit", "events", "legacy"} <= names


@case("ensure_tables")
def h_idempotent(mod):
    f = need(mod, "ensure_tables")
    md, _ = _events()
    with database(SEED) as (engine, path):
        assert f(engine, md) == ["events"]
        assert f(engine, md) == ["events"]
        assert rows(path, "SELECT COUNT(*) FROM events") == [(4,)], "existing data must be kept"


@case("insert_many")
def h_insert_persists(mod):
    f = need(mod, "insert_many")
    _, t = _events()
    with database(EVENTS_DDL) as (engine, path):
        n = f(engine, t, [{"kind": "click", "actor": "a"}, {"kind": "view", "actor": "b"},
                          {"kind": "click", "actor": "c"}])
        assert n == 3
        assert rows(path, "SELECT kind, actor FROM events ORDER BY id") == [
            ("click", "a"), ("view", "b"), ("click", "c")], "inserted rows must be committed"


@case("insert_many")
def h_insert_empty_and_generator(mod):
    f = need(mod, "insert_many")
    _, t = _events()
    with database(EVENTS_DDL) as (engine, path):
        assert f(engine, t, []) == 0
        assert rows(path, "SELECT COUNT(*) FROM events") == [(0,)]
        assert f(engine, t, ({"kind": "k%d" % i, "actor": "x"} for i in range(4))) == 4
        assert rows(path, "SELECT COUNT(*) FROM events") == [(4,)]


@case("delete_matching")
def h_delete_persists(mod):
    f = need(mod, "delete_matching")
    _, t = _events()
    with database(SEED) as (engine, path):
        assert f(engine, t, kind="click") == 2
        assert rows(path, "SELECT kind, actor FROM events ORDER BY id") == [("view", "ann"), ("view", "cy")], \
            "the deletion must be committed"


@case("delete_matching")
def h_delete_multi_criteria(mod):
    f = need(mod, "delete_matching")
    _, t = _events()
    with database(SEED) as (engine, path):
        assert f(engine, t, kind="view", actor="ann") == 1
        assert f(engine, t, kind="view", actor="nobody") == 0
        assert rows(path, "SELECT COUNT(*) FROM events") == [(3,)]


@case("delete_matching")
def h_delete_requires_criteria(mod):
    f = need(mod, "delete_matching")
    _, t = _events()
    with database(SEED) as (engine, path):
        try:
            f(engine, t)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError without criteria")
        assert rows(path, "SELECT COUNT(*) FROM events") == [(4,)]


@case("count_rows")
def h_count(mod):
    f = need(mod, "count_rows")
    _, t = _events()
    with database(SEED) as (engine, _):
        assert f(engine, t) == 4
        assert f(engine, t, kind="click") == 2
        assert f(engine, t, kind="click", actor="bob") == 1
        assert f(engine, t, actor="zed") == 0
