"""Sales reporting queries over the customers/invoices tables."""
from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table, func, select, text

metadata = MetaData()

customers = Table(
    "customers", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(80), nullable=False),
    Column("region", String(20), nullable=False),
)

invoices = Table(
    "invoices", metadata,
    Column("id", Integer, primary_key=True),
    Column("customer_id", Integer, ForeignKey("customers.id"), nullable=False),
    Column("amount", Integer, nullable=False),
    Column("issued_on", String(10), nullable=False),  # ISO date
)


def totals_by_customer(conn):
    """Return {customer name: total invoiced amount} for customers with at least one invoice."""
    stmt = (select(customers.c.name, func.sum(invoices.c.amount))
            .select_from(customers.join(invoices))
            .group_by(customers.c.name))
    return {name: total for name, total in conn.execute(stmt)}


def big_spenders(conn, min_total):
    """[(name, total)] of customers whose invoices sum to at least `min_total`, largest first
    (ties by name)."""
    totals = (select(invoices.c.customer_id, func.sum(invoices.c.amount).label("total"))
              .group_by(invoices.c.customer_id))
    stmt = (select(customers.c.name, totals.c.total)
            .where(customers.c.id == totals.c.customer_id)
            .where(totals.c.total >= min_total)
            .order_by(totals.c.total.desc(), customers.c.name))
    return [(name, total) for name, total in conn.execute(stmt)]


def count_matching(conn, stmt):
    """Number of rows the SELECT statement `stmt` would return."""
    return conn.execute(select(func.count()).select_from(stmt.alias())).scalar()


def monthly_revenue(conn):
    """[(YYYY-MM, total)] of invoiced amounts per calendar month, in month order."""
    rows = conn.execute(text(
        "SELECT substr(issued_on, 1, 7) AS month, SUM(amount) AS total "
        "FROM invoices GROUP BY month ORDER BY month"))
    return [(month, total) for month, total in rows]
