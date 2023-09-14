import asyncio
import psycopg2 as ps
import pytest
from httpx import AsyncClient

from app.src.main import app
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.config import DB_NAME, DB_PASS, DB_USER, DB_PORT
from app.src.db import conn_db

DB_HOST = "localhost"

DSN = (
    f"dbname={DB_NAME} user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT}"
)

DSN_TEST = (
    f"dbname=test_db user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT}"
)


def create_db():
    conn = ps.connect(DSN)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    print("Creating Database")
    cursor.execute("CREATE DATABASE test_db")
    cursor.close()
    conn.close()


def delete_db():
    conn = ps.connect(DSN)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    print("Deleting Database")
    cursor.execute("DROP DATABASE test_db")
    cursor.close()
    conn.close()


def init_tables():
    sql_script_path = "./init.sql"
    item_csv_path = r"C:\Users\Denis\Desktop\restaurant\back\app\tests\items.csv"
    try:
        conn = ps.connect(DSN_TEST)
        cursor = conn.cursor()
        with open(sql_script_path, "r") as script_file:
            sql_script = script_file.read()
            cursor.execute(sql_script)
        cursor.execute(f"COPY public.item FROM '{item_csv_path}' DELIMITER ',' CSV HEADER;")
        conn.commit()
        conn.close()
    except ps.Error as e:
        delete_db()
        raise Exception(f"Error initializing the test database: {e}")
    

async def startup_db():
    app.state.conn_db = conn_db
    app.state.pool = await app.state.conn_db.get_database_pool(DSN)


async def startup_test_db():
    app.state.conn_db = conn_db
    app.state.pool = await app.state.conn_db.get_database_pool(DSN_TEST)


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    create_db()
    init_tables()
    app.dependency_overrides[startup_db] = startup_test_db
    pool = await conn_db.get_database_pool(DSN_TEST)
    app.state.pool = pool
    yield
    app.state.pool = await conn_db.close_database_pool()
    delete_db()


@pytest.fixture
async def ac():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
