import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _db import database, rows  # noqa: E402
from sa_testlib import case, need  # noqa: E402
from sqlalchemy import Column, Integer, String, inspect  # noqa: E402
from sqlalchemy.orm import Session, declarative_base  # noqa: E402

Base = declarative_base()


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True)
    body = Column(String(50), nullable=False)


def _db():
    return database("CREATE TABLE notes (id INTEGER PRIMARY KEY, body VARCHAR(50) NOT NULL);"
                    "INSERT INTO notes (id, body) VALUES (1, 'first'), (2, 'second');")


def _add(session, body):
    session.add(Note(body=body))
    session.flush()
    return body.upper()


def _boom(session):
    session.add(Note(body="doomed"))
    session.flush()
    raise ValueError("boom")


@case("factory_config")
def h_factory_no_expire(mod):
    with _db() as (engine, path):
        s = need(mod, "make_session_factory")(engine)()
        n = Note(body="kept")
        s.add(n)
        s.commit()
        s.close()
        assert n.body == "kept", "attributes must stay readable after commit/close"
        assert rows(path, "SELECT COUNT(*) FROM notes") == [(3,)]


@case("factory_config")
def h_factory_no_autoflush(mod):
    with _db() as (engine, _):
        s = need(mod, "make_session_factory")(engine)()
        try:
            s.add(Note(body="pending"))
            assert s.query(Note).count() == 2, "pending objects must not be autoflushed"
            assert s.bind is engine
        finally:
            s.rollback()
            s.close()


@case("session_scope")
def h_scope_commit(mod):
    with _db() as (engine, path):
        with need(mod, "session_scope")(lambda: Session(engine)) as s:
            s.add(Note(body="third"))
        assert rows(path, "SELECT body FROM notes ORDER BY id") == [("first",), ("second",), ("third",)]
        assert len(s.identity_map) == 0, "session must be closed"


@case("session_scope")
def h_scope_rollback(mod):
    with _db() as (engine, path):
        try:
            with need(mod, "session_scope")(lambda: Session(engine)) as s:
                s.add(Note(body="lost"))
                s.flush()
                raise KeyError("x")
        except KeyError:
            pass
        else:
            raise AssertionError("exception must propagate")
        assert rows(path, "SELECT COUNT(*) FROM notes") == [(2,)]


@case("run_in_transaction")
def h_txn_flushes_not_commits(mod):
    with _db() as (engine, path):
        s = Session(engine)
        try:
            assert need(mod, "run_in_transaction")(s, _add, "fresh") == "FRESH"
            with s.no_autoflush:
                assert s.query(Note).filter(Note.body == "fresh").count() == 1, "work must be flushed"
            assert rows(path, "SELECT COUNT(*) FROM notes") == [(2,)], "must not commit"
            s.commit()
            assert rows(path, "SELECT body FROM notes WHERE id = 3") == [("fresh",)]
        finally:
            s.close()


@case("run_in_transaction")
def h_txn_joins_outer(mod):
    with _db() as (engine, path):
        s = Session(engine)
        try:
            s.add(Note(body="outer"))
            s.flush()
            assert need(mod, "run_in_transaction")(s, _add, "inner") == "INNER"
            assert need(mod, "run_in_transaction")(s, _add, "inner2") == "INNER2"
            assert rows(path, "SELECT COUNT(*) FROM notes") == [(2,)], "must not commit the outer transaction"
            s.rollback()
            assert rows(path, "SELECT COUNT(*) FROM notes") == [(2,)]
            assert s.query(Note).count() == 2
        finally:
            s.close()


@case("run_in_transaction")
def h_txn_error(mod):
    with _db() as (engine, path):
        s = Session(engine)
        try:
            s.add(Note(body="pending"))
            try:
                need(mod, "run_in_transaction")(s, _boom)
            except ValueError:
                pass
            else:
                raise AssertionError("exception must propagate")
            s.rollback()
            s.commit()
            assert rows(path, "SELECT body FROM notes ORDER BY id") == [("first",), ("second",)]
        finally:
            s.close()


@case("query_to_dicts")
def h_query_dicts(mod):
    with _db() as (engine, _):
        s = Session(engine)
        try:
            f = need(mod, "query_to_dicts")
            assert f(s, s.query(Note.id, Note.body).order_by(Note.id)) == [
                {"id": 1, "body": "first"}, {"id": 2, "body": "second"}]
            assert f(s, s.query(Note.body.label("text")).filter(Note.id == 2)) == [{"text": "second"}]
            assert f(s, s.query(Note.id).filter(Note.id > 5)) == []
        finally:
            s.close()


@case("shutdown")
def h_shutdown(mod):
    with _db() as (engine, _):
        s1, s2 = Session(engine), Session(engine)
        a = s1.query(Note).filter(Note.id == 1).one()
        b = s2.query(Note).filter(Note.id == 2).one()
        need(mod, "shutdown")()
        assert a not in s1 and b not in s2
        assert inspect(a).detached and inspect(b).detached
