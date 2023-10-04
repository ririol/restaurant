from fastapi import APIRouter

from app.src.db import conn_db
from app.src.admin.controllers import AdminController
from app.src.admin.schemas import ItemIn

admin_router = APIRouter(prefix="/admin")


@admin_router.get("/stats/")
async def get_statistic():
    return await AdminController.get_stats(conn_db)


@admin_router.get("/items/")
async def get_items():
    return await AdminController.get_list_of_items(conn_db)


@admin_router.get("/orders/")
async def get_all_orders():
    return await AdminController.get_all_orders(conn_db)


# TODO: bonus
@admin_router.post("/items/")
async def add_item(item: ItemIn):
    return await AdminController.add_item(conn_db, item)


@admin_router.get("/menu/")
async def get_menu():
    return await AdminController.get_menu(conn_db)
