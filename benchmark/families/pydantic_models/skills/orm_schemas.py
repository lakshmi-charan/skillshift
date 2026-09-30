"""API schemas populated from ORM objects (written against pydantic 1.10)."""
from typing import List

from pydantic import BaseModel, parse_obj_as


class UserSchema(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True


class LineItemSchema(BaseModel):
    sku: str
    quantity: int

    class Config:
        orm_mode = True


class OrderSchema(BaseModel):
    id: int
    customer: UserSchema
    items: List[LineItemSchema] = []

    class Config:
        orm_mode = True


def user_from_orm(obj):
    """Build a UserSchema from an ORM object (any object exposing the fields as attributes)."""
    return UserSchema.from_orm(obj)


def orders_from_orm(objs):
    """Build a list of OrderSchema (with nested customer and items) from ORM order objects."""
    return parse_obj_as(List[OrderSchema], list(objs))


def user_from_dict(data):
    """Build a UserSchema from a plain dict (e.g. a decoded JSON request body)."""
    return UserSchema.parse_obj(data)


def field_names(model):
    """Names of the fields declared on a pydantic model class, in declaration order."""
    return list(model.__fields__)


def required_fields(model):
    """Names of the fields of a pydantic model class that must be supplied (no default)."""
    return [name for name, field in model.__fields__.items() if field.required]
