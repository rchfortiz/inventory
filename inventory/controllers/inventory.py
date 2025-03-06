from typing import Annotated

from fastapi import APIRouter, Body, Request

from inventory.controllers.templates import template
from inventory.database import DatabaseDep
from inventory.services.item import delete_item, edit_item, get_item, get_items
from inventory.services.user import GetUserDep

inventory_router = APIRouter()


@inventory_router.get("/inventory")
async def page(request: Request, db: DatabaseDep, user: GetUserDep):
    return template(
        request,
        "inventory",
        {"username": user.name, "role": user.role, "items": await get_items(db)},
    )


@inventory_router.get("/items/{item_id}")
async def item(request: Request, _: GetUserDep, db: DatabaseDep, item_id: int):
    return template(request, "item", {"item": await get_item(db, item_id)})


@inventory_router.put("/items/{item_id}")
async def edit(
    _: GetUserDep,
    db: DatabaseDep,
    item_id: int,
    name: Annotated[str, Body(embed=True)],
):
    await edit_item(db, item_id, name=name)
    return "OK"


@inventory_router.delete("/items/{item_id}")
async def delete(_: GetUserDep, db: DatabaseDep, item_id: int):
    await delete_item(db, item_id)
    return "OK"
