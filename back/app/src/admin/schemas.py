from pydantic import BaseModel, NonNegativeFloat

from app.src.restaurant.schemas import (
    ConversationInDB,
    ItemInDB,
    OrderInDB,
)


class OrderWithItems(BaseModel):
    order: OrderInDB
    items: list[ItemInDB]
    replics: list[ConversationInDB]


class OrderStat(BaseModel):
    order_count: int
    all_order_total: float
    avg_order_price: float


class ItemStats(BaseModel):
    name: str
    count: int


class UpsellStats(BaseModel):
    question_asked: int
    accepted: int
    denied: int
    total: float


class Stats(BaseModel):
    order_stats: OrderStat
    item_stats: list[ItemStats]
    upsell_stat: UpsellStats


class ItemIn(BaseModel):
    name: str
    count: int
    is_primary: bool
    price: NonNegativeFloat
