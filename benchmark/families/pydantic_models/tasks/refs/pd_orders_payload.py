from typing import List

from pydantic import BaseModel


class _Customer(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True


class _Item(BaseModel):
    sku: str
    quantity: int

    class Config:
        orm_mode = True


class _Order(BaseModel):
    id: int
    customer: _Customer
    items: List[_Item]

    class Config:
        orm_mode = True


def orders_payload(orders):
    return [_Order.from_orm(o).dict() for o in orders]
