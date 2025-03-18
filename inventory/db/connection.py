from sqlalchemy import create_engine
from sqlmodel import SQLModel

from inventory.settings import settings

engine = create_engine(settings.db_url)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
