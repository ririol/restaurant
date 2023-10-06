from app.src.db import ConnectionDB
from app.src.admin.schemas import ItemInDB, ItemIn, OrderInDB


class AdminController:
    @staticmethod
    async def get_all_orders(db: ConnectionDB):
        # order: list[OrderInDB]
        # items: list[ItemInDB]
        # replics: list[ConversationInDB]
        stmt = """
                SELECT * FROM public.order o 
                WHERE o.is_closed = true
                ORDER BY o.id ASC;
                """
        orders = [OrderInDB(**order) for order in await db.fetch_rows(stmt)]

        stmt = """
                SELECT json_agg(jsonb_build_object(
                    'id', i.id,
                    'name', i.name,
                    'count', i.count,
                    'is_primary', i.is_primary,
                    'price', i.price,
                    'is_upselled', oi.is_upselled
                )) as items
                FROM public.order o
                INNER JOIN order_items oi ON oi.order_id = o.id
                INNER JOIN item i ON oi.item_id = i.id
                WHERE o.is_closed = true
                GROUP BY o.id
                ORDER BY o.id ASC;
                """

        items =await db.fetch_rows(stmt)

        stmt = """
                SELECT json_agg(c) as conversations
                FROM conversation c
                INNER JOIN public.order o ON o.id = c.order_id AND o.is_closed = true
                GROUP BY o.id
                ORDER BY o.id ASC;
                """

        conversations = await db.fetch_rows(stmt)


        return {"orders": orders, "item": items, "conversation": conversations}

    @staticmethod
    async def get_stats(db: ConnectionDB):
        stmt = f"""
                    SELECT
                        COUNT(o.id)  as order_count,
                        SUM(o.total) as all_order_total,
                        AVG(o.total) as avg_order_price
                    FROM public.order o
                    WHERE o.is_closed = true;
                    """
        order_stats = await db.fetch_rows(stmt)
        stmt = """
                WITH item_counts AS (
                SELECT i.name, COUNT(oi.item_id) AS count
                FROM item i
                JOIN order_items oi ON oi.item_id = i.id
                GROUP BY i.name
                )
                SELECT COALESCE(json_agg(json_build_object('name', name, 'count', count)), '{}'::json) AS items_count
                FROM item_counts AS ordered_items;
                """
        items_ordered = await db.fetch_rows(stmt)
        stmt = """
                SELECT
                    (SELECT COUNT(*) FROM conversation WHERE replica ~ 'What is a')             AS question_asked,
                    
                    COUNT(*) FILTER (WHERE c.replica = 'Yes, please.' AND o.is_closed = true)   AS accepted,
                    COUNT(*) FILTER (WHERE c.replica = 'No, thank you.' AND o.is_closed = true) AS denied,
                    (SELECT COALESCE(SUM(i.price), 0)
                    FROM item i
                    JOIN order_items oi ON oi.item_id = i.id
                    WHERE oi.is_upselled = true)                                                AS total
                FROM
                    conversation c
                JOIN
                    public.order o ON c.order_id = o.id;
                """

        upsell_stats = await db.fetch_rows(stmt)
        return {
            "order_stats": order_stats[0],
            "item_stats": items_ordered[0]["items_count"],
            "upsell_stat": upsell_stats[0],
        }

    @staticmethod
    async def get_list_of_items(db: ConnectionDB) -> list[ItemInDB]:
        stmt = f"""
                SELECT *
                FROM item AS i
                ORDER BY i.id;
                """
        result = await db.fetch_rows(stmt)
        return [ItemInDB(**db_item) for db_item in result]

    @staticmethod
    async def get_menu(db: ConnectionDB):
        stmt = f"""
                SELECT *
                FROM item
                ORDER BY id, is_primary ASC;
               """
        result = await db.fetch_rows(stmt)
        return result

    @staticmethod
    async def add_item(db: ConnectionDB, item: ItemIn):
        stmt = f"""
                INSERT INTO item (name, count, is_primary, price)
                VALUES ('{item.name}', {item.count}, {item.is_primary}, {item.price})
                ON CONFLICT (name)
                DO UPDATE SET
                    count = EXCLUDED.count,
                    is_primary = EXCLUDED.is_primary,
                    price = EXCLUDED.price;
                """
        await db.fetch_rows(stmt)
