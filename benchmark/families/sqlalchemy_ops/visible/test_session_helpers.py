from sa_testlib import case, need
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String(20))


def _factory(mod):
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    return need(mod, "make_session_factory")(engine)


@case("session_scope")
def test_scope(mod):
    factory = _factory(mod)
    with need(mod, "session_scope")(factory) as s:
        s.add(Item(name="a"))
    with need(mod, "session_scope")(factory) as s:
        assert s.query(Item).count() == 1


@case("run_in_transaction")
def test_run(mod):
    factory = _factory(mod)
    s = factory()
    need(mod, "run_in_transaction")(s, lambda sess: sess.add(Item(name="b")))
    assert factory().query(Item).count() == 1


@case("query_to_dicts")
def test_dicts(mod):
    factory = _factory(mod)
    s = factory()
    s.add(Item(name="c"))
    s.commit()
    assert need(mod, "query_to_dicts")(s, s.query(Item.name)) == [{"name": "c"}]
