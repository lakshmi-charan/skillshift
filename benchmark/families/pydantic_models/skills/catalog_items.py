"""Catalogue items with constrained fields (written against pydantic 1.10)."""
from typing import List

from pydantic import BaseModel, Field, ValidationError, condecimal, conint, constr, validator


class Item(BaseModel):
    sku: str
    name: constr(strip_whitespace=True, min_length=1, max_length=60)
    price: condecimal(gt=0, max_digits=10, decimal_places=2)
    stock: conint(ge=0) = 0
    tags: List[str] = Field(default_factory=list, max_items=5)

    class Config:
        allow_mutation = False

    @validator("tags", pre=True)
    def split_tags(cls, value):
        if isinstance(value, str):
            value = value.split(",")
        return [tag.strip().lower() for tag in value if tag.strip()]


def make_item(**fields):
    """Create a validated Item. Raises ValidationError (a ValueError) if a field is invalid."""
    return Item(**fields)


def try_parse_item(data):
    """Return an Item built from the dict `data`, or None if the data is not a valid item."""
    try:
        return Item.parse_obj(data)
    except ValidationError:
        return None
