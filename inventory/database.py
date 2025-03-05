from pathlib import Path

from databases import Database

from inventory.settings import settings

database = Database(settings.database_url)
init_script = Path("inventory/init.sql").read_text()


async def prepare_tables():
    for stmt in init_script.split(";"):
        await database.execute(stmt)
