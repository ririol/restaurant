from fastapi import APIRouter, WebSocket

from app.src.db import conn_db
from .controllers import OrderController, WebscoketConroller
from app.src.restaurant.schemas import ConversationIn, ConversationInDB


guest_router = APIRouter(prefix="/guest")


@guest_router.get("/start_conversation/")
async def start_conversation() -> ConversationInDB:
    order_id = await OrderController.create_order(conn_db)
    replica = "Welcome, what can I get you?"
    conv = ConversationIn(order_id=order_id, owner="bot", replica=replica)

    return await OrderController.write_replica(conn_db, conv)


@guest_router.post("/dialog/")
async def dialog(conv_in: ConversationIn) -> ConversationInDB:
    await OrderController.write_replica(conn_db, conv_in)
    conv_in.replica = conv_in.replica.strip()
    # check is it upsell stage, must be first in my implementation
    # rewrite in future
    if await OrderController.was_suggested(conn_db, conv_in.order_id):
        return await upsell(conn_db, conv_in)

    if "I'd like a" in conv_in.replica:
        return await OrderController.add_item(conn_db, conv_in)

    elif "I don't want a" in conv_in.replica:
        return await OrderController.discard_item(conn_db, conv_in)

    elif "That's all." == conv_in.replica:
        return await OrderController.close_conversation(conn_db, conv_in)

    elif "What is a" in conv_in.replica:
        return await OrderController._chat_gpt_describe_answer(conn_db, conv_in)

    else:
        return await OrderController._error_answer(conn_db, conv_in.order_id)


async def upsell(conn_db, conv_in: ConversationIn) -> ConversationInDB:
    if "Yes, please." == conv_in.replica:  # item is added by default
        await OrderController.set_was_suggested(conn_db, conv_in.order_id, "false")
        return await OrderController._suggest_next_item_answer(
            conn_db, conv_in.order_id
        )

    elif "No, thank you." == conv_in.replica:  # item that was suggsted would be deleted
        await OrderController.set_was_suggested(conn_db, conv_in.order_id, "false")
        return await OrderController.discard_last_item(conn_db, conv_in)

    else:
        return await OrderController._error_answer(conn_db, conv_in.order_id)


@guest_router.get("/get_commands/")
async def get_commands():
    commands = {
        1: "I'd like a X.",
        2: "I don't want a X.",
        3: "That's all.",
        4: "Yes, please.",
        5: "No, thank you.",
        6: "What is a X?",
    }
    return commands


@guest_router.get("/get_menu/")
async def get_menu():
    return await OrderController.get_menu(conn_db)


@guest_router.websocket("/ws")
async def websocket_reminder(websocket: WebSocket):
    await WebscoketConroller.start(websocket) 