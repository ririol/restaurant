from app.src.db import ConnectionDB
from app.src.admin.schemas import OrderWithItems, ItemInDB, Stats


class AdminController:
    @staticmethod
    async def get_all_orders(db: ConnectionDB) -> list[OrderWithItems]:
        # order: OrderInDB
        # items: list[ItemInDB]
        # replics: list[ConversationInDB]
        stmt = f"""
                SELECT json_agg(
                    jsonb_build_object(
                        'order', row_to_json(o.*),
                        'items', (
                            SELECT json_agg(row_to_json(i.*))
                            FROM public.item i
                            INNER JOIN order_items oi ON oi.item_id = i.id
                            WHERE oi.order_id = o.id
                        ),
                        'replics', (
                            SELECT json_agg(row_to_json(c.*))
                            FROM public.conversation c
                            WHERE c.order_id = o.id
                        )
                    )
                ) AS orders
                FROM public.order o;
                """
        result = await db.fetch_rows(stmt)
        order_all_included = [OrderWithItems(**i) for i in result[0][0]]
        return order_all_included

    @staticmethod
    async def get_stats(db: ConnectionDB):
        stmt = f"""
                SELECT
                    json_build_object(
                        'order_stats', row_to_json(stat),
                        'item_stats', (
                            SELECT json_agg(row_to_json(total_amount))
                            FROM (
                                SELECT i.name, count(oi.item_id)
                                FROM item i
                                JOIN order_items oi ON oi.item_id = i.id
                                GROUP BY i.name
                            ) AS total_amount
                        ),
                        'upsell_stat', json_build_object(
                            'question_asked', (SELECT count(*) FROM conversation WHERE replica ~ 'What is [A-Za-z0-9_]+\\?'),
                            'accepted', (SELECT count(*) FROM conversation WHERE replica = 'Yes, please.'),
                            'denied', (SELECT count(*) FROM conversation WHERE replica = 'No, thank you.'),
                            'total', (SELECT COALESCE(SUM(i.price), 0)
                                FROM item i
                                JOIN order_items oi ON oi.item_id = i.id
                                WHERE oi.is_upselled = true)
                        )
                    )
                FROM (
                    SELECT 
                        count(o.id) as order_count,
                        sum(o.total) as all_order_total,
                        avg(o.total) as avg_order_price
                    FROM public.order o
                ) AS stat;
                """
        result = await db.fetch_rows(stmt)
        print(result[0][0])
        stat = Stats(**result[0][0])
        return stat

    @staticmethod
    async def get_list_of_items(db: ConnectionDB) -> list[ItemInDB]:
        stmt = f"""
                SELECT ROW_TO_JSON(i.*) 
                FROM item AS i
                ORDER BY i.id;
                """
        result = await db.fetch_rows(stmt)
        return [ItemInDB(**i[0]) for i in result]
