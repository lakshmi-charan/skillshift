import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _taskdb import make_db  # noqa: E402
from sa_testlib import case, need  # noqa: E402

DB = """
CREATE TABLE sales (id INTEGER PRIMARY KEY, region TEXT, amount INTEGER);
INSERT INTO sales (region, amount) VALUES ('north', 10), ('north', 25), ('south', 35), ('east', 5),
  ('west', 20), ('west', 1);
"""


@case("functional")
def t_threshold(mod):
    path = make_db(DB)
    try:
        f = need(mod, "region_totals")
        assert f("sqlite:///" + path, 21) == [("north", 35), ("south", 35), ("west", 21)]
        assert f("sqlite:///" + path, 36) == []
    finally:
        os.remove(path)


@case("functional")
def t_all(mod):
    path = make_db(DB)
    try:
        out = need(mod, "region_totals")("sqlite:///" + path, 0)
        assert [tuple(r) for r in out] == [("north", 35), ("south", 35), ("west", 21), ("east", 5)]
    finally:
        os.remove(path)
