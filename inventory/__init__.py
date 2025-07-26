from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from .admin import admin_router
from .borrower import borrower_router
from .db.connection import create_db_and_tables
from .item import item_router
from .log import log_router
from .user import Staff, user_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(user_router)
app.include_router(item_router)
app.include_router(borrower_router)
app.include_router(admin_router)
app.include_router(log_router)


@app.get("/")
async def index(_: Staff) -> RedirectResponse:
    return RedirectResponse("/items")
