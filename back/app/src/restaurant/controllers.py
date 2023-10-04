from app.src.db import ConnectionDB
from app.src.restaurant.schemas import (
    ConversationIn,
    ConversationInDB,
    ItemInDB,
    OrderInDB,
)
from app.src.restaurant.open_ai_request import get_item_description

SPECIAL_SYMBOLS = "!@#$%^&*()_+{}\[\]:;<>,.?~\\|`\"'"


class OrderController:
    @staticmethod
    async def create_order(db: ConnectionDB) -> int:
        stmt = "INSERT INTO public.order DEFAULT VALUES RETURNING id;"
        order_id = await db.fetch_rows(stmt)
        return order_id[0]["id"]

    @staticmethod
    async def write_replica(db: ConnectionDB, conv: ConversationIn) -> ConversationInDB:
        stmt = f"""
                INSERT INTO public.conversation (order_id, owner, replica) 
                VALUES (%s, %s, %s)
                RETURNING public.conversation.*
                """
        values = (conv.order_id, conv.owner, conv.replica)
        result = await db.fetch_rows(stmt, values)
        conv_db = ConversationInDB(**result[0])

        return conv_db

    # potential sql injection, im not sure how python slice str from pydantic field
    # rewrite stmt with using query parameters provide by aiopg
    @staticmethod
    async def _get_item_by_name(db: ConnectionDB, conv_in: ConversationIn):
        item_pos = conv_in.replica.find(" a")
        item_name = conv_in.replica[item_pos + 3 :].strip()
        translation_table = str.maketrans("", "", SPECIAL_SYMBOLS)
        cleaned_item_name = item_name.translate(translation_table)
        stmt = f"""
                SELECT item.*
                FROM item
                WHERE name = '{cleaned_item_name}'
                """
        result = await db.fetch_rows(stmt)
        
        # TODO: create it as exception to avoid type hint errors
        if not result:
            return result
        return ItemInDB(**result[0])

    @staticmethod
    async def _error_answer(db: ConnectionDB, conv_id: int):
        replica = "I don't understand."
        conv_answer = ConversationIn(order_id=conv_id, owner="bot", replica=replica)

        return await OrderController.write_replica(db, conv_answer)

    @staticmethod
    async def _no_item_answer(db: ConnectionDB, order_id: int, item_name: str):
        replica = f"I’m sorry but we’re out of {item_name}"
        conv_out = ConversationIn(order_id=order_id, owner="bot", replica=replica)

        return await OrderController.write_replica(db, conv_out)

    @staticmethod
    async def _suggest_next_item_answer(db: ConnectionDB, order_id: int):
        replica = "Would you like anything else?"
        conv_out = ConversationIn(order_id=order_id, owner="bot", replica=replica)

        return await OrderController.write_replica(db, conv_out)

    @staticmethod
    async def _upsell_item_answer(
        db: ConnectionDB, order_id: int, upsell_item: ItemInDB
    ):
        replica = (
            f"Would you like to add a {upsell_item.name} for ${upsell_item.price}?"
        )
        conv_out = ConversationIn(order_id=order_id, owner="bot", replica=replica)

        return await OrderController.write_replica(db, conv_out)

    @staticmethod
    async def _close_conversation_answer(
        db: ConnectionDB, conv_in: ConversationIn, order: OrderInDB
    ):
        replica = f"Your total is ${order.total}. Thank you and have a nice day!"
        conv_out = ConversationIn(
            order_id=conv_in.order_id, owner="bot", replica=replica
        )
        return await OrderController.write_replica(db, conv_out)

    @staticmethod
    async def _empty_order_answer(db: ConnectionDB, conn_id: int):
        replica = f"Your order is empty. Please order something to end conversation"
        conv_out = ConversationIn(order_id=conn_id, owner="bot", replica=replica)
        return await OrderController.write_replica(db, conv_out)

    @staticmethod
    async def _chat_gpt_describe_answer(db: ConnectionDB, conv_in: ConversationIn):
        item: ItemInDB = await OrderController._get_item_by_name(db, conv_in)  # type: ignore
        if not item:
            return await OrderController._error_answer(db, conv_in.order_id)
        openai_answer = await get_item_description(item.name)
        conv_out = ConversationIn(
            order_id=conv_in.order_id, owner="bot", replica=openai_answer
        )
        return await OrderController.write_replica(db, conv_out)

    @staticmethod
    async def _add_random_upsell_item_to_order(db: ConnectionDB, order_id: int):
        stmt = f"""
                SELECT item.*
                FROM item
                WHERE is_primary = false
                ORDER BY RANDOM()
                LIMIT 1
                """
        result = await db.fetch_rows(stmt)
        upsell_item = ItemInDB(**result[0])
        stmt = f"""
                INSERT INTO public.order_items (order_id, item_id, is_upselled)
                VALUES ({order_id}, {upsell_item.id}, true);
                """
        await db.fetch_rows(stmt)
        await OrderController.set_was_suggested(db, order_id, "true")
        # TODO: provide a(an) logic
        return await OrderController._upsell_item_answer(db, order_id, upsell_item)

    @staticmethod
    async def get_order(db: ConnectionDB, order_id: int) -> OrderInDB:
        stmt = f"""
                SELECT public.order.*
                FROM public.order
                WHERE id = {order_id} 
                """
        result = await db.fetch_rows(stmt)
        order = OrderInDB(**result[0])

        return order

    @staticmethod
    async def set_was_suggested(db: ConnectionDB, order_id: int, bools: str):
        stmt = f"""
                UPDATE public.order 
                SET was_suggested = {bools} 
                WHERE id = {order_id}
                RETURNING was_suggested;
                """
        result = await db.fetch_rows(stmt)

    @staticmethod
    async def was_suggested(db: ConnectionDB, order_id: int) -> bool:
        stmt = f"""
                SELECT was_suggested
                FROM public.order
                WHERE id = {order_id}
                """
        result = await db.fetch_rows(stmt)

        return result[0]["was_suggested"]

    @staticmethod
    async def get_order_length(db: ConnectionDB, order_id: int) -> int:
        stmt = f"""
                SELECT COUNT(*)
                FROM order_items
                WHERE order_id = {order_id};
                """
        result = await db.fetch_rows(stmt)
        order_len = result[0]["count"]
        return order_len

    @staticmethod
    async def add_item(db: ConnectionDB, conv_in: ConversationIn):
        order_id = conv_in.order_id
        item: ItemInDB = await OrderController._get_item_by_name(db, conv_in)  # type: ignore

        if not item:
            return await OrderController._error_answer(db, order_id)

        if item.count <= 0:
            return await OrderController._no_item_answer(db, order_id, item.name)

        stmt = f"""
                INSERT INTO public.order_items (order_id, item_id)
                VALUES ({order_id}, {item.id});
                """
        await db.fetch_rows(stmt)

        upsell_item = await OrderController.check_upsell(db, order_id)
        order_len = await OrderController.get_order_length(db, order_id)

        if upsell_item and order_len == 1:
            return await OrderController._add_random_upsell_item_to_order(db, order_id)

        return await OrderController._suggest_next_item_answer(db, order_id)

    @staticmethod
    async def check_upsell(db: ConnectionDB, order_id: int) -> bool:
        stmt = f"""
                SELECT 
                    CASE 
                        WHEN EXISTS (
                            SELECT 1
                            FROM order_items oi
                            JOIN item i ON oi.item_id = i.id
                            WHERE oi.order_id = {order_id} AND i.is_primary = false
                        ) THEN false
                        ELSE true
                    END AS is_item_primary
                FROM
                    public.order o
                WHERE 
                    o.id = {order_id}
                """
        result = await db.fetch_rows(stmt)

        return result[0]["is_item_primary"]

    @staticmethod
    async def close_conversation(db: ConnectionDB, conv_in: ConversationIn):
        order = await OrderController.get_order(db, conv_in.order_id)
        if order.total == 0.0:
            return await OrderController._empty_order_answer(db, conv_in.order_id)
        stmt = f"""
                UPDATE public.order
                SET is_closed = true
                WHERE id = {conv_in.order_id}
                """
        await db.fetch_rows(stmt)

        return await OrderController._close_conversation_answer(db, conv_in, order)

    @staticmethod
    async def discard_item(db: ConnectionDB, conv_in: ConversationIn):
        item: ItemInDB = await OrderController._get_item_by_name(db, conv_in)  # type: ignore
        if not item:
            return await OrderController._error_answer(db, conv_in.order_id)

        order_length = await OrderController._check_order_length(db, conv_in)
        if order_length == 0:
            return await OrderController._error_answer(db, conv_in.order_id)

        stmt = f"""
                DELETE FROM order_items 
                WHERE id in (
                    SELECT id
                    FROM order_items
                    WHERE item_id = {item.id}
                    ORDER BY id desc
                    LIMIT 1);
                """
        await db.fetch_rows(stmt)

        return await OrderController._suggest_next_item_answer(db, conv_in.order_id)

    @staticmethod
    async def _check_order_length(db: ConnectionDB, conv_in: ConversationIn) -> int:
        stmt = f"""
                SELECT COUNT(item_id)
                FROM order_items 
                WHERE order_id = {conv_in.order_id};
                """
        result = await db.fetch_rows(stmt)
        order_len = result[0]["count"]
        return order_len

    @staticmethod
    async def discard_last_item(db: ConnectionDB, conv_in: ConversationIn):
        order_length = await OrderController._check_order_length(db, conv_in)
        if order_length == 0:
            return await OrderController._error_answer(db, conv_in.order_id)

        stmt = f"""
                DELETE FROM order_items 
                WHERE id in (
                    SELECT id 
                    FROM order_items
                    ORDER BY id desc
                    LIMIT 1);
                """
        await db.fetch_rows(stmt)

        return await OrderController._suggest_next_item_answer(db, conv_in.order_id)

    @staticmethod
    async def get_list_of_items(db: ConnectionDB) -> list[ItemInDB]:
        stmt = f"""
                SELECT i.*
                FROM item AS i
                ORDER BY i.id;
                """
        result = await db.fetch_rows(stmt)
        return [ItemInDB(**i) for i in result]

    @staticmethod
    async def get_menu(db: ConnectionDB):
        stmt = f"""
                SELECT name, price
                FROM (
                  SELECT name, price
                  FROM item
                  ORDER BY is_primary DESC
                ) AS sorted_data; 
                """
        result = await db.fetch_rows(stmt)
        return result
