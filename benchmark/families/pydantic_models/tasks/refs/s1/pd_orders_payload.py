from typing import List

from pydantic import BaseModel, ConfigDict


class _Customer(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str


class _Item(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sku: str
    quantity: int


class _Order(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    customer: _Customer
    items: List[_Item]


def orders_payload(orders):
    return [_Order.model_validate(o).model_dump() for o in orders]
