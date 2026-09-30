import os
import tempfile

from sa_testlib import case, need
from sqlalchemy import create_engine


def _engine():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    engine = create_engine("sqlite:///" + path)
    engine.execute("CREATE TABLE sales (region TEXT, amount INTEGER)")
    engine.execute("INSERT INTO sales VALUES ('north', 10), ('north', 5), ('south', 7)")
    return engine, path


@case("run_report")
def test_run_report(mod):
    engine, path = _engine()
    try:
        out = need(mod, "run_report")(engine, "SELECT region, SUM(amount) FROM sales GROUP BY region ORDER BY region")
        assert out == [("north", 15), ("south", 7)]
    finally:
        engine.dispose()
        os.remove(path)


@case("report_scalar")
def test_scalar(mod):
    engine, path = _engine()
    try:
        assert need(mod, "report_scalar")(engine, "SELECT SUM(amount) FROM sales WHERE region = :r", {"r": "south"}) == 7
    finally:
        engine.dispose()
        os.remove(path)


@case("render_table")
def test_render(mod):
    assert need(mod, "render_table")(["a", "b"], [(1, 2)]) == "a | b\n--+--\n1 | 2"
