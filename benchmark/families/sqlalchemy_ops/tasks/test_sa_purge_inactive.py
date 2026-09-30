import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _taskdb import make_db, rows  # noqa: E402
from sa_testlib import case, need  # noqa: E402

DB = """
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, last_seen TEXT);
INSERT INTO customers (name, last_seen) VALUES ('ann', '2023-12-31'), ('bob', '2024-03-01'),
  ('cy', '2022-06-15'), ('dee', '2024-01-01');
"""


@case("functional")
def t_purge_persists(mod):
    path = make_db(DB)
    try:
        assert need(mod, "purge_inactive")("sqlite:///" + path, "2024-01-01") == 2
        assert rows(path, "SELECT name FROM customers ORDER BY id") == [("bob",), ("dee",)], \
            "deletion must be committed"
    finally:
        os.remove(path)


@case("functional")
def t_nothing_to_purge(mod):
    path = make_db(DB)
    try:
        assert need(mod, "purge_inactive")("sqlite:///" + path, "2000-01-01") == 0
        assert rows(path, "SELECT COUNT(*) FROM customers") == [(4,)]
    finally:
        os.remove(path)
