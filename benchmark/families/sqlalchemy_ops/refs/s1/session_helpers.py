"""Session / unit-of-work helpers shared by the application."""
from contextlib import contextmanager

from sqlalchemy.orm import Session, sessionmaker


def make_session_factory(engine):
    """Session factory bound to `engine`: no autoflush, attributes stay loaded after commit."""
    return sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


@contextmanager
def session_scope(factory):
    """Provide a session that is committed on success, rolled back on error, and always closed."""
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def run_in_transaction(session, fn, *args, **kwargs):
    """Call fn(session, *args, **kwargs) as a unit of work inside the session's transaction and return
    its result. The work is flushed but not committed (the caller owns the transaction); if fn raises,
    the transaction is rolled back and the exception propagates."""
    try:
        result = fn(session, *args, **kwargs)
        session.flush()
    except Exception:
        session.rollback()
        raise
    return result


def query_to_dicts(session, query):
    """Execute a column-based Query and return its rows as dicts keyed by column label."""
    return [dict(row) for row in session.execute(query).mappings()]


def shutdown():
    """Close every Session in the process (used at application shutdown and between tests)."""
    Session.close_all()
