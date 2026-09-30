"""Ad-hoc SQL report queries against the application database."""
from sqlalchemy import text


def run_report(engine, sql, params=None):
    """Execute a SQL string with named ``:param`` placeholders and return all rows as a list of tuples."""
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        return [tuple(row) for row in result]


def report_scalar(engine, sql, params=None):
    """Execute a SQL string and return the first column of the first row (None if there are no rows)."""
    with engine.connect() as conn:
        return conn.execute(text(sql), params or {}).scalar()


def report_columns(engine, sql, params=None):
    """Return the column names produced by a SQL string, in order."""
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        try:
            return list(result.keys())
        finally:
            result.close()


def render_table(headers, rows):
    """Render headers and rows as a fixed-width text table (None is shown as an empty cell)."""
    cells = [[str(h) for h in headers]]
    cells += [["" if v is None else str(v) for v in row] for row in rows]
    widths = [max(len(r[i]) for r in cells) for i in range(len(headers))]
    lines = [" | ".join(c.ljust(w) for c, w in zip(r, widths)).rstrip() for r in cells]
    lines.insert(1, "-+-".join("-" * w for w in widths))
    return "\n".join(lines)
