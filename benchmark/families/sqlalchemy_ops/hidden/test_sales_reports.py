import contextlib
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _db import database  # noqa: E402
from sa_testlib import case, need  # noqa: E402
from sqlalchemy import select  # noqa: E402

SEED = """
INSERT INTO customers (id, name, region) VALUES (1, 'Ann', 'north'), (2, 'Bob', 'south'), (3, 'Cy', 'north'),
  (4, 'Dee', 'east');
INSERT INTO invoices (customer_id, amount, issued_on) VALUES
  (1, 100, '2024-01-05'), (1, 50, '2024-02-10'), (2, 120, '2024-01-20'), (3, 30, '2024-02-01'),
  (3, 120, '2024-03-03');
"""


@contextlib.contextmanager
def _conn(mod):
    with database() as (engine, path):
        need(mod, "metadata").create_all(engine)
        con = sqlite3.connect(path)
        con.executescript(SEED)
        con.commit()
        con.close()
        with engine.connect() as conn:
            yield conn


@case("totals_by_customer")
def h_totals(mod):
    with _conn(mod) as conn:
        assert need(mod, "totals_by_customer")(conn) == {"Ann": 150, "Bob": 120, "Cy": 150}


@case("big_spenders")
def h_big(mod):
    f = need(mod, "big_spenders")
    with _conn(mod) as conn:
        assert f(conn, 130) == [("Ann", 150), ("Cy", 150)]
        assert f(conn, 0) == [("Ann", 150), ("Cy", 150), ("Bob", 120)]


@case("big_spenders")
def h_big_none(mod):
    f = need(mod, "big_spenders")
    with _conn(mod) as conn:
        assert f(conn, 151) == []
        assert f(conn, 150) == [("Ann", 150), ("Cy", 150)]


@case("count_matching")
def h_count(mod):
    f = need(mod, "count_matching")
    with _conn(mod) as conn:
        c, i = mod.customers, mod.invoices
        assert f(conn, select(c).where(c.c.region == "north")) == 2
        assert f(conn, select(i.c.id).where(i.c.amount >= 100)) == 3
        assert f(conn, select(c.c.name).where(c.c.region == "west")) == 0


@case("count_matching")
def h_count_grouped(mod):
    f = need(mod, "count_matching")
    with _conn(mod) as conn:
        i = mod.invoices
        assert f(conn, select(i.c.customer_id).group_by(i.c.customer_id)) == 3


@case("monthly_revenue")
def h_monthly(mod):
    with _conn(mod) as conn:
        assert need(mod, "monthly_revenue")(conn) == [("2024-01", 220), ("2024-02", 80), ("2024-03", 120)]
