from sqlalchemy import create_engine, text


def query_dicts(db_url, sql, params=None):
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            return [dict(row._mapping) for row in conn.execute(text(sql), params or {})]
    finally:
        engine.dispose()
