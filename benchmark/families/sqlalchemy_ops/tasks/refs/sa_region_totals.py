from sqlalchemy import create_engine, text


def region_totals(db_url, min_total):
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT region, SUM(amount) AS total FROM sales GROUP BY region "
                "HAVING SUM(amount) >= :min_total ORDER BY total DESC, region"), {"min_total": min_total})
            return [(region, total) for region, total in result]
    finally:
        engine.dispose()
