"""API schemas populated from ORM objects."""
from typing import List

from pydantic import BaseModel, ConfigDict, TypeAdapter


class UserSchema(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class LineItemSchema(BaseModel):
    sku: str
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class OrderSchema(BaseModel):
    id: int
    customer: UserSchema
    items: List[LineItemSchema] = []

    model_config = ConfigDict(from_attributes=True)


def user_from_orm(obj):
    """Build a UserSchema from an ORM object (any object exposing the fields as attributes)."""
    return UserSchema.model_validate(obj)


def orders_from_orm(objs):
    """Build a list of OrderSchema (with nested customer and items) from ORM order objects."""
    return TypeAdapter(List[OrderSchema]).validate_python(list(objs), from_attributes=True)


def user_from_dict(data):
    """Build a UserSchema from a plain dict (e.g. a decoded JSON request body)."""
    return UserSchema.parse_obj(data)


def field_names(model):
    """Names of the fields declared on a pydantic model class, in declaration order."""
    return list(model.model_fields)


def required_fields(model):
    """Names of the fields of a pydantic model class that must be supplied (no default)."""
    return [name for name, field in model.model_fields.items() if field.is_required()]
