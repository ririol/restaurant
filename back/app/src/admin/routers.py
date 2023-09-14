from fastapi import APIRouter

from app.src.db import conn_db
from app.src.admin.controllers import AdminController 

admin_router = APIRouter(prefix="/admin")

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


@admin_router.get("/")
async def get_statistic():
    pass


@admin_router.get("/items/")
async def get_items():
    return await AdminController.get_list_of_items(conn_db)



#bonus
@admin_router.post("/items/")
async def add_item():
    pass

