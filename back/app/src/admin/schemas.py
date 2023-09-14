from pydantic import BaseModel

from app.src.restaurant.schemas import ConversationIn, ConversationInDB, ItemInDB, OrderInDB


# Admin view
# The admin view should display the following:
#   The list of all submitted orders with:
#   Their total
#   List of all ordered items
#   The entire conversation history

# The general order stats, including:
#   Total amount of orders, total revenue
#   Average order price
#   Total amount ordered for each item on the menu
#   Upsell stats - questions asked, accepted, rejected, total upsell revenue. ???????

class OrderWithItems(BaseModel):
    order: OrderInDB
    items: list[ItemInDB]
    replics: list[ConversationInDB]


class OrderList(BaseModel):
    list_of_orders: list[OrderWithItems]
    
    
class Statistic(BaseModel):
    total_orders: int
    avg_order_price: int
    item_order_times: dict[str, int]
    