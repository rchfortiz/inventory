from typing import Annotated

from fastapi import APIRouter, Body, Request

from inventory.controllers.templates import template
from inventory.services.item import delete_item, edit_item, get_item, get_items

inventory_router = APIRouter()


@inventory_router.get("/inventory")
async def page(request: Request):
    return template(request, "inventory", {"role": "admin", "items": await get_items()})


@inventory_router.get("/items/{item_id}")
async def item(request: Request, item_id: int):
    return template(request, "item", {"item": await get_item(item_id)})


@inventory_router.put("/items/{item_id}")
async def edit(
    item_id: int,
    name: Annotated[str, Body(embed=True)],
):
    await edit_item(item_id, name=name)
    return "OK"


@inventory_router.delete("/items/{item_id}")
async def delete(item_id: int):
    await delete_item(item_id)
    return "OK"
