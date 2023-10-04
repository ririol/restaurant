import aiopg
import psycopg2

# import asyncio
from app.config import DB_HOST, DB_NAME, DB_PASS, DB_USER, DB_PORT

DSN = (
    f"dbname={DB_NAME} user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT}"
)


class ConnectionDB:
    def __init__(self) -> None:
        self.pool: aiopg.Pool

    async def get_database_pool(self, dsn):
        self.pool = await aiopg.create_pool(dsn)  # type: ignore
        return self.pool

    async def close_database_pool(self) -> None:
        self.pool.close()
        await self.pool.wait_closed()

    async def get_db(self) -> aiopg.Connection:
        conn = await self.pool.acquire()
        return conn

    async def release_db(self, conn: aiopg.Connection) -> None:
        self.pool.release(conn)

    # async def fetch_rows(self, query: str, values=None) -> list[tuple] | list:
    #     async with self.pool.acquire() as conn:
    #         async with conn.cursor() as cur:
    #             await cur.execute(query, values)
    #             try:
    #                 result = await cur.fetchall()
    #             except psycopg2.ProgrammingError:
    #                 return []
    #             return result

    async def fetch_rows(self, query: str, values=None) -> list[dict] | list:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, values)
                try:
                    result = await cur.fetchall()
                    columns = [desc[0] for desc in cur.description]  # type: ignore
                    data_list = [dict(zip(columns, row)) for row in result]
                except psycopg2.ProgrammingError:
                    return []
                return data_list


conn_db = ConnectionDB()

# async def get_select():
#     conn_db.pool = await aiopg.create_pool(DSN)
#     stmt = f"""
#             SELECT
#                 COUNT(o.id) as order_count,
#                 SUM(o.total) as all_order_total,
#                 AVG(o.total) as avg_order_price
#             FROM public.order o;
#             """
#     order_stats = await conn_db.fetch_rows(stmt)
#     stmt = """
#             WITH item_counts AS (
#               SELECT i.name, COUNT(oi.item_id) AS count
#               FROM item i
#               JOIN order_items oi ON oi.item_id = i.id
#               GROUP BY i.name
#             )
#             SELECT COALESCE(json_agg(json_build_object('name', name, 'count', count)), '{}'::json) AS items_count
#             FROM item_counts AS ordered_items;
#             """
#     items_ordered = await conn_db.fetch_rows(stmt)
#     stmt = """
#             SELECT
#                 (SELECT count(*) FROM conversation WHERE replica ~ 'What is [A-Za-z0-9_]+\\?')  AS question_asked,
#                 (SELECT count(*) FROM conversation WHERE replica = 'Yes, please.')              AS accepted,
#                 (SELECT count(*) FROM conversation WHERE replica = 'No, thank you.')            AS denied,
#                 (SELECT COALESCE(SUM(i.price), 0)
#                             FROM item i
#                             JOIN order_items oi ON oi.item_id = i.id
#                             WHERE oi.is_upselled = true)                                        AS total_upsell_amount
#            """

#     upsell_stats = await conn_db.fetch_rows(stmt)
#     return {"order_stats":order_stats[0], "item_stats": items_ordered[0], "upsell_stat": upsell_stats[0]}

# if __name__ == "__main__":
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#     a = asyncio.run(get_select())
#     print(a)
#     asyncio.run(conn_db.close_database_pool())
