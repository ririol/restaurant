from fastapi import APIRouter

from app.src.db import conn_db
from .controllers import OrderController
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
        "I'd like a(an) X.",
        "I don't want a(an) X.",
        "That's all.",
        "Yes, please.",
        "No, thank you.",
        "What is X?",
    }
    return commands


@guest_router.get("/get_menu/")
async def get_menu():
    return await OrderController.get_menu(conn_db)
