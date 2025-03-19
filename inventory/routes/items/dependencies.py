from typing import Annotated

from fastapi import Depends
from sqlmodel import select

from inventory.db.connection import DBSessionDep
from inventory.db.models import Item
from inventory.routes import items_redirect_exception


def get_item(db: DBSessionDep, item_id: int) -> Item:
    item = db.exec(select(Item).where(Item.id == item_id)).first()
    if not item:
        raise items_redirect_exception
    return item


ItemDep = Annotated[Item, Depends(get_item)]
