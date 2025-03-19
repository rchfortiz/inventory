from collections.abc import Generator
from contextlib import suppress
from typing import Annotated

from bcrypt import gensalt, hashpw
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel

from inventory.db.models import Role, User
from inventory.settings import settings

engine = create_engine(settings.db_url)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        admin = User(username="admin", password_hash=hashpw(b"admin", gensalt()), role=Role.ADMIN)
        session.add(admin)
        with suppress(IntegrityError):
            session.commit()


def get_db_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session


DBSessionDep = Annotated[Session, Depends(get_db_session)]
