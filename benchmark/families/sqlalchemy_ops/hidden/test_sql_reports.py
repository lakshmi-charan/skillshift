import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _db import database  # noqa: E402
from sa_testlib import case, need  # noqa: E402

SALES = """
CREATE TABLE sales (id INTEGER PRIMARY KEY, region TEXT NOT NULL, amount INTEGER NOT NULL, sold_on TEXT NOT NULL);
INSERT INTO sales (region, amount, sold_on) VALUES
  ('north', 10, '2024-01-03'), ('north', 5, '2024-02-01'), ('south', 7, '2024-01-15'), ('east', 1, '2024-03-01');
"""


@case("run_report")
def h_grouped_with_param(mod):
    f = need(mod, "run_report")
    with database(SALES) as (engine, _):
        out = f(engine, "SELECT region, SUM(amount) AS total FROM sales GROUP BY region "
                        "HAVING SUM(amount) > :min ORDER BY region", {"min": 5})
    assert out == [("north", 15), ("south", 7)], out
    assert all(type(r) is tuple for r in out)


@case("run_report")
def h_no_params(mod):
    f = need(mod, "run_report")
    with database(SALES) as (engine, _):
        assert f(engine, "SELECT COUNT(*) FROM sales") == [(4,)]
        assert f(engine, "SELECT region FROM sales WHERE region = :r ORDER BY id", {"r": "west"}) == []


@case("run_report")
def h_string_param(mod):
    f = need(mod, "run_report")
    with database(SALES) as (engine, _):
        out = f(engine, "SELECT amount, sold_on FROM sales WHERE region = :r AND sold_on >= :d ORDER BY id",
                {"r": "north", "d": "2024-01-01"})
    assert out == [(10, "2024-01-03"), (5, "2024-02-01")]


@case("report_scalar")
def h_scalar(mod):
    f = need(mod, "report_scalar")
    with database(SALES) as (engine, _):
        assert f(engine, "SELECT SUM(amount) FROM sales WHERE region = :r", {"r": "north"}) == 15
        assert f(engine, "SELECT COUNT(*) FROM sales") == 4


@case("report_scalar")
def h_scalar_empty(mod):
    f = need(mod, "report_scalar")
    with database(SALES) as (engine, _):
        assert f(engine, "SELECT amount FROM sales WHERE region = :r", {"r": "west"}) is None


@case("report_columns")
def h_columns(mod):
    f = need(mod, "report_columns")
    with database(SALES) as (engine, _):
        assert f(engine, "SELECT region, amount AS total FROM sales") == ["region", "total"]
        assert f(engine, "SELECT sold_on FROM sales WHERE amount > :a", {"a": 100}) == ["sold_on"]


@case("render_table")
def h_render(mod):
    f = need(mod, "render_table")
    out = f(["region", "total"], [("north", 15), ("south", None)])
    assert out == "region | total\n-------+------\nnorth  | 15\nsouth  |", repr(out)


@case("render_table")
def h_render_wide_cells(mod):
    f = need(mod, "render_table")
    out = f(["a", "b"], [("long value", 1), ("x", 12345)])
    assert out.splitlines() == ["a          | b", "-----------+------", "long value | 1", "x          | 12345"], out


@case("render_table")
def h_render_empty(mod):
    f = need(mod, "render_table")
    assert f(["id", "name"], []) == "id | name\n---+-----"
