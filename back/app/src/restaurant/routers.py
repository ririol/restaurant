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


@guest_router.post("/add_item/")
async def dialog(conv_in: ConversationIn) -> ConversationInDB:
    await OrderController.write_replica(conn_db, conv_in)

    if "I'd like a" in conv_in.replica:
        return await OrderController.add_item(conn_db, conv_in)

    elif "I don't want a" in conv_in.replica:
        return await OrderController.discard_item(conn_db, conv_in)
    
    elif "That's all." == conv_in.replica:
        return await OrderController.close_conversation(conn_db, conv_in)
    #elif "What is a" in conv_in.replica:
    #    pass  # TODO: create OpenAI client for request
    else:
        return await OrderController._error_answer(conn_db, conv_in.order_id)

@guest_router.post("/upsell_item/")
async def upsell(conv_in: ConversationIn):
    if "No, thank you." == conv_in.replica:  # item that was suggsted would be deleted
        return await OrderController.discard_last_item(conn_db, conv_in)

    elif "Yes, please." == conv_in.replica:  # item is adding by default
        return await OrderController._suggest_next_item_answer(conn_db, conv_in.order_id)
    
    else:
        return await OrderController._error_answer(conn_db, conv_in.order_id)