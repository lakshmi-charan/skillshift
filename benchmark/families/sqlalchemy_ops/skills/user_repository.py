"""ORM models and repository helpers for users and their orders (written against SQLAlchemy 1.4)."""
from sqlalchemy import Column, ForeignKey, Integer, String, select
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(120), nullable=False, unique=True)

    orders = relationship("Order", back_populates="user", order_by="Order.id")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), nullable=False, default="new")
    total = Column(Integer, nullable=False, default=0)  # cents

    user = relationship("User", back_populates="orders")


def create_schema(engine):
    Base.metadata.create_all(engine)


def add_user(session, name, email):
    """Persist a new user (email stored lower-case) and return its id."""
    user = User(name=name, email=email.lower())
    session.add(user)
    session.commit()
    return user.id


def add_order(session, user_id, total, status="new"):
    """Persist a new order for `user_id` and return its id."""
    order = Order(user_id=user_id, total=total, status=status)
    session.add(order)
    session.commit()
    return order.id


def find_by_email(session, email):
    """Return the User with this email (case-insensitive input) or None."""
    return session.query(User).filter_by(email=email.lower()).first()


def get_user(session, user_id):
    """Return the User with primary key `user_id` or None."""
    return session.query(User).get(user_id)


def orders_for(session, email, status=None):
    """Orders of the user with this email, optionally only those with `status`, ordered by id."""
    q = session.query(Order).join("user").filter(User.email == email.lower())
    if status is not None:
        q = q.filter(Order.status == status)
    return q.order_by(Order.id).all()


def owner_of_order(session, order_id):
    """Return the User who placed order `order_id`, or None if there is no such order."""
    stmt = select(User).join(User.orders).filter_by(id=order_id)
    return session.execute(stmt).scalars().first()
