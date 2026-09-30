from sqlalchemy import create_engine, text


def order_owner_email(db_url, order_id):
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            return conn.execute(text("SELECT users.email FROM orders JOIN users ON users.id = orders.user_id "
                                     "WHERE orders.id = :oid"), {"oid": order_id}).scalar()
    finally:
        engine.dispose()
