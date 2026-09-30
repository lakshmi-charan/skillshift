"""Version-neutral fixtures for the sqlalchemy_ops hidden tests: temp-file SQLite databases are seeded and
inspected with the stdlib sqlite3 module, so the checks never depend on the SQLAlchemy API under test."""
import contextlib
import os
import sqlite3
import tempfile

from sqlalchemy import create_engine


def new_db(script=""):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    if script:
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


@contextlib.contextmanager
def database(script=""):
    """Yield (engine, path) for a fresh temp-file database seeded with `script`."""
    path = new_db(script)
    engine = create_engine("sqlite:///" + path)
    try:
        yield engine, path
    finally:
        engine.dispose()
        try:
            os.remove(path)
        except OSError:
            pass


def expect_error(fn, *exc):
    try:
        fn()
    except exc or Exception:
        return
    raise AssertionError("expected an exception")
