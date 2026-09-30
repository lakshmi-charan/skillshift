"""Bulk operations on Core tables (written against SQLAlchemy 1.4)."""
from sqlalchemy import and_, func, inspect, select


def ensure_tables(engine, metadata):
    """Create any missing tables of `metadata` and return the sorted table names in the database."""
    metadata.create_all(engine)
    return sorted(inspect(engine).get_table_names())


def insert_many(engine, table, rows):
    """Insert a list of row dicts into `table`; return the number of rows inserted."""
    rows = list(rows)
    if not rows:
        return 0
    engine.execute(table.insert(), rows)
    return len(rows)


def _criteria(table, criteria):
    return and_(*[table.c[name] == value for name, value in criteria.items()])


def delete_matching(engine, table, **criteria):
    """Delete the rows whose columns equal all the given values; return the number of rows deleted."""
    if not criteria:
        raise ValueError("refusing to delete without criteria")
    with engine.connect() as conn:
        result = conn.execute(table.delete().where(_criteria(table, criteria)))
        return result.rowcount


def count_rows(engine, table, **criteria):
    """Count the rows of `table`, optionally only those whose columns equal the given values."""
    stmt = select([func.count()]).select_from(table)
    if criteria:
        stmt = stmt.where(_criteria(table, criteria))
    return engine.execute(stmt).scalar()
