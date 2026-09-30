from sa_testlib import case, need
from sqlalchemy import create_engine, text


def _conn():
    engine = create_engine("sqlite://")
    conn = engine.connect()
    conn.execute(text("CREATE TABLE t (id INTEGER, name TEXT)"))
    conn.execute(text("INSERT INTO t VALUES (1, 'a'), (2, 'b')"))
    return conn


@case("fetch_dicts")
def test_dicts(mod):
    conn = _conn()
    assert need(mod, "fetch_dicts")(conn, text("SELECT id, name FROM t ORDER BY id")) == \
        [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]
    conn.close()


@case("fetch_column")
def test_column(mod):
    conn = _conn()
    assert need(mod, "fetch_column")(conn, text("SELECT id, name FROM t ORDER BY id"), "name") == ["a", "b"]
    conn.close()


@case("row_has_column")
def test_has_column(mod):
    conn = _conn()
    row = conn.execute(text("SELECT id, name FROM t")).first()
    assert need(mod, "row_has_column")(row, "name")
    assert row.keys() == ["id", "name"]
    conn.close()
