from sqlalchemy import create_engine, text


def purge_inactive(db_url, cutoff):
    engine = create_engine(db_url)
    try:
        with engine.begin() as conn:
            result = conn.execute(text("DELETE FROM customers WHERE last_seen < :cutoff"), {"cutoff": cutoff})
            return result.rowcount
    finally:
        engine.dispose()
