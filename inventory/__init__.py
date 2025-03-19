from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from inventory.db.connection import create_db_and_tables
from inventory.routes.auth.dependencies import StaffDep
from inventory.routes.auth.routes import auth_router
from inventory.routes.borrowers.routes import borrowers_router
from inventory.routes.items.routes import items_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(items_router)
app.include_router(borrowers_router)


@app.get("/")
async def index(_: StaffDep) -> RedirectResponse:
    return RedirectResponse("/items")
