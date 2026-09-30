"""Shared fixture for the sqlalchemy_ops task tests (stdlib sqlite3 only)."""
import os
import sqlite3
import tempfile


def make_db(script):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = sqlite3.connect(path)
    con.executescript(script)
    con.commit()
    con.close()
    return path


def rows(path, sql, params=()):
    con = sqlite3.connect(path)
    try:
        return con.execute(sql, params).fetchall()
    finally:
        con.close()
