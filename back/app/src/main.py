from fastapi import FastAPI

from app.src.db import conn_db, DSN
from app.src.restaurant.routers import guest_router
from app.src.admin.routers import admin_router

app = FastAPI()

app.include_router(guest_router)
app.include_router(admin_router)

@app.on_event("startup")
async def startup_db():
    app.state.conn_db = conn_db
    app.state.pool = await app.state.conn_db.get_database_pool(DSN)


@app.on_event("shutdown")
async def shutdown_db():
    await app.state.conn_db.close_database_pool()
