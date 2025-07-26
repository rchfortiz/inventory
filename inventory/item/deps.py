from typing import Annotated

from fastapi import Depends
from sqlmodel import select

from inventory.db.connection import DBSession
from inventory.db.models import Item

from .redirect import redirect_to_items_exception


def get_item(db: DBSession, item_id: int) -> Item:
    item = db.exec(select(Item).where(Item.id == item_id)).first()
    if not item:
        raise redirect_to_items_exception
    return item


ItemDep = Annotated[Item, Depends(get_item)]
