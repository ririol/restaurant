import asyncio
from httpx import AsyncClient

from app.src.restaurant.schemas import ConversationInDB, ConversationIn

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


item_id_db = [
    {"id": 1, "name": "Croissant",    "count": 100, "is_primary": True,  "price": 2.14},
    {"id": 2, "name": "Cheesecake",   "count": 100, "is_primary": True,  "price": 1.45},
    {"id": 3, "name": "Donut",        "count": 100, "is_primary": True,  "price": 2.54},
    {"id": 4, "name": "Cinnamon bun", "count": 100, "is_primary": True,  "price": 3.1},
    {"id": 5, "name": "Coffee",       "count": 100, "is_primary": False, "price": 0.7},
]
default = lambda order_id: {"order_id": order_id, "owner": "user"}

async def test_empty_db_after_init(ac: AsyncClient):
    response = await ac.get("/admin/items/")
    assert response.json() == item_id_db


async def start_order(ac: AsyncClient):
    response = await ac.get("/guest/start_conversation/")
    assert response.status_code == 200
    conv_bot = ConversationInDB(**response.json())

    replica =                                                       "I'd like a Croissant"
    conv_user = {**default(conv_bot.order_id), "replica": replica}
    response = await ac.post("/guest/add_item/", json=conv_user)
    
    conv_bot = ConversationInDB(**response.json())
    assert conv_bot.replica ==                                      "Would you like to add a Coffee for $0.7?"
    return conv_bot.order_id

async def test_order_suggested_item_accept(ac: AsyncClient):
    order_id = await start_order(ac)
    replica = "Yes, please."
    conv_user = {**default(order_id), "replica": replica}
    response = await ac.post("/guest/add_item/", json=conv_user)
    
    conv_bot = ConversationInDB(**response.json())
    assert conv_bot.replica == "Would you like anything else?"
    
    replica = "That's all."
    conv_user = {**default(order_id), "replica": replica}
    response = await ac.post("/guest/add_item/", json=conv_user)
    conv_bot = ConversationInDB(**response.json())
    
    assert conv_bot.replica == "Your total is $2.84. Thank you and have a nice day!"

async def test_order_suggested_item_deny(ac: AsyncClient):
    order_id = await start_order(ac)
    replica = "No, thank you."
    conv_user = {**default(order_id), "replica": replica}
    response = await ac.post("/guest/add_item/", json=conv_user)
    
    conv_bot = ConversationInDB(**response.json())
    assert conv_bot.replica == "Would you like anything else?"
    
    replica = "That's all."
    conv_user = {**default(order_id), "replica": replica}
    response = await ac.post("/guest/add_item/", json=conv_user)
    conv_bot = ConversationInDB(**response.json())
    
    assert conv_bot.replica == "Your total is $2.14. Thank you and have a nice day!"
    
async def test_run_out_of_item(ac: AsyncClient):
    order_id = await start_order(ac)
    replica = "No, thank you."
    conv_user = {**default(order_id), "replica": replica}
    response = await ac.post("/guest/add_item/", json=conv_user)

    conv_bot = ConversationInDB(**response.json())
    assert conv_bot.replica == "Would you like anything else?"
    replica =                                                       "I'd like a Croissant"
    conv_user = {**default(order_id), "replica": replica}
    for i in range(98):
        response = await ac.post("/guest/add_item/", json=conv_user)
    response = await ac.post("/guest/add_item/", json=conv_user)
    conv_bot = ConversationInDB(**response.json())
    
    assert conv_bot.replica == "I’m sorry but we’re out of Croissant"
    
    replica = "That's all."
    conv_user = {**default(order_id), "replica": replica}
    response = await ac.post("/guest/add_item/", json=conv_user)
    conv_bot = ConversationInDB(**response.json())
    
    assert conv_bot.replica == f"Your total is ${98*2.14}. Thank you and have a nice day!"
    

async def test_order_first_item_secondary(ac: AsyncClient):
    response = await ac.get("/guest/start_conversation/")
    assert response.status_code == 200
    conv_bot = ConversationInDB(**response.json())

    replica =                                                       "I'd like a Coffee"
    conv_user = {**default(conv_bot.order_id), "replica": replica}
    response = await ac.post("/guest/add_item/", json=conv_user)
    
    conv_bot = ConversationInDB(**response.json())
    assert conv_bot.replica ==                                      "Would you like anything else?"