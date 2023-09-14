import datetime
from pydantic import BaseModel, NonNegativeFloat, Field
from typing import Literal


class ItemInDB(BaseModel):
    id: int
    name: str
    count: int
    is_primary: bool
    price: NonNegativeFloat


class OrderInDB(BaseModel):
    id: int
    total: NonNegativeFloat
    time: datetime.datetime
    was_suggested: bool
    is_closed: bool


class OrderItem(BaseModel):
    order_id: int
    item_id: int


class ConversationInDB(BaseModel):
    order_id: int
    time: datetime.datetime
    owner: Literal["user", "bot"]
    replica: str = Field(max_length=256)


class ConversationIn(BaseModel):
    order_id: int
    owner: Literal["user", "bot"]
    replica: str = Field(max_length=256)
