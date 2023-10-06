import aiopg
import psycopg2

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

