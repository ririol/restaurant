from app.src.db import ConnectionDB
from app.src.admin.schemas import OrderWithItems, ItemInDB

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

class AdminController:
    @staticmethod
    async def get_all_orders(db: ConnectionDB) -> OrderWithItems:
        stmt = f"""
                SELECT ROW_TO_JSON('order', list_of_items, conversation)
                FROM (
                    SELECT public.order as 'order'
                    
                )
                """

    # order: OrderInDB
    # items: list[ItemInDB]
    # replics: list[ConversationInDB]

# """
# SELECT
#     JSON_AGG(o.*) as order,
#     JSON_AGG(i.*) AS items,
#     JSON_AGG(c.*) AS conversation
# FROM
#     public.order o
# JOIN
#     order_items aoi ON o.id = aoi.order_id
# JOIN
#     item i ON aoi.item_id = i.id
# JOIN
#     conversation c ON o.id = c.order_id
# GROUP BY
#     o.id;"""

    @staticmethod
    async def get_list_of_items(db: ConnectionDB) -> list[ItemInDB]:
        stmt = f"""
                SELECT ROW_TO_JSON(i.*) 
                FROM item AS i
                ORDER BY i.id;
                """
        result = await db.fetch_rows(stmt)
        return [ItemInDB(**i[0]) for i in result]