import os
import tempfile

from sa_testlib import case, need
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, func, select


def _setup():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    engine = create_engine("sqlite:///" + path)
    md = MetaData()
    t = Table("events", md, Column("id", Integer, primary_key=True), Column("kind", String(20)))
    md.create_all(engine)
    return engine, path, t


@case("insert_many")
def test_insert(mod):
    engine, path, t = _setup()
    try:
        assert need(mod, "insert_many")(engine, t, [{"kind": "a"}, {"kind": "b"}]) == 2
        assert engine.execute(select([func.count()]).select_from(t)).scalar() == 2
    finally:
        engine.dispose()
        os.remove(path)


@case("delete_matching")
def test_delete(mod):
    engine, path, t = _setup()
    try:
        engine.execute(t.insert(), [{"kind": "a"}, {"kind": "b"}, {"kind": "a"}])
        assert need(mod, "delete_matching")(engine, t, kind="a") == 2
        assert [r["kind"] for r in engine.execute(t.select())] == ["b"]
    finally:
        engine.dispose()
        os.remove(path)


@case("count_rows")
def test_count(mod):
    engine, path, t = _setup()
    try:
        engine.execute(t.insert(), [{"kind": "a"}, {"kind": "b"}])
        assert need(mod, "count_rows")(engine, t, kind="b") == 1
    finally:
        engine.dispose()
        os.remove(path)
