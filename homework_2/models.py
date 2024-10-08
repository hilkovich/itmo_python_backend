from typing import List
from pydantic import BaseModel


class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False


class ItemCart(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool


class Cart(BaseModel):
    id: int
    items: List[ItemCart] = []
    price: float = 0.0


class ItemAdd(BaseModel):
    name: str
    price: float
