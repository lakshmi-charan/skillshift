"""Helpers for turning Core result rows into plain Python data (written against SQLAlchemy 1.4)."""


def fetch_dicts(conn, stmt):
    """Execute `stmt` on connection `conn`; return each row as a dict keyed by column name."""
    return [dict(row) for row in conn.execute(stmt)]


def fetch_column(conn, stmt, name):
    """Execute `stmt` and return the values of the column called `name`, in row order."""
    return [row[name] for row in conn.execute(stmt)]


def fetch_tuples(conn, stmt):
    """Execute `stmt` and return each row as a plain tuple."""
    return [tuple(row) for row in conn.execute(stmt)]


def row_has_column(row, name):
    """True if the result row has a column called `name`."""
    return name in row


def result_keys(conn, stmt):
    """Return the column names of the result of `stmt`, in order."""
    result = conn.execute(stmt)
    try:
        return list(result.keys())
    finally:
        result.close()
