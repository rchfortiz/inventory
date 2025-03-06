from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from databases import Database
from fastapi import Depends, FastAPI

from inventory.settings import settings

db = Database(settings.database_url)
init_script = Path("inventory/init.sql").read_text()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await db.connect()
    await run_init_script(db)
    yield
    await db.disconnect()


async def get_db() -> Database:
    return db


DatabaseDep = Annotated[Database, Depends(get_db)]


async def run_init_script(db: Database):
    for stmt in init_script.split(";"):
        await db.execute(stmt)
