import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _taskdb import make_db  # noqa: E402
from sa_testlib import case, need  # noqa: E402

DB = """
CREATE TABLE stores (id INTEGER PRIMARY KEY, city TEXT, region TEXT, staff INTEGER);
INSERT INTO stores (city, region, staff) VALUES ('Leeds', 'north', 12), ('York', 'north', 4),
  ('Bath', 'south', 7);
"""


@case("functional")
def t_params(mod):
    path = make_db(DB)
    try:
        out = need(mod, "query_dicts")("sqlite:///" + path,
                                       "SELECT city, staff FROM stores WHERE region = :region ORDER BY city",
                                       {"region": "north"})
        assert out == [{"city": "Leeds", "staff": 12}, {"city": "York", "staff": 4}]
        assert all(type(d) is dict for d in out)
    finally:
        os.remove(path)


@case("functional")
def t_no_params(mod):
    path = make_db(DB)
    try:
        f = need(mod, "query_dicts")
        assert f("sqlite:///" + path, "SELECT COUNT(*) AS n, SUM(staff) AS s FROM stores") == [{"n": 3, "s": 23}]
        assert f("sqlite:///" + path, "SELECT city FROM stores WHERE staff > :m", {"m": 100}) == []
    finally:
        os.remove(path)
