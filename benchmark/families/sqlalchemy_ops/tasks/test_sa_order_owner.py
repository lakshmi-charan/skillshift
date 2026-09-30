import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _taskdb import make_db  # noqa: E402
from sa_testlib import case, need  # noqa: E402

DB = """
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT);
CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id), total INTEGER);
INSERT INTO users (id, name, email) VALUES (1, 'Ann', 'ann@example.com'), (2, 'Bob', 'bob@example.com');
INSERT INTO orders (id, user_id, total) VALUES (1, 2, 10), (2, 1, 20), (3, 2, 30);
"""


@case("functional")
def t_owner(mod):
    path = make_db(DB)
    try:
        f = need(mod, "order_owner_email")
        url = "sqlite:///" + path
        assert f(url, 1) == "bob@example.com"
        assert f(url, 2) == "ann@example.com"
        assert f(url, 3) == "bob@example.com"
    finally:
        os.remove(path)


@case("functional")
def t_missing(mod):
    path = make_db(DB)
    try:
        assert need(mod, "order_owner_email")("sqlite:///" + path, 42) is None
    finally:
        os.remove(path)
