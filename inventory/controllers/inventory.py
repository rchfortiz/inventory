from typing import Annotated

from fastapi import APIRouter, Body, Request

from inventory.controllers.templates import template

inventory_router = APIRouter()

items = [
    {
        "id": 1,
        "name": "Magnifying Glass",
        "total_quantity": 20,
        "available_quantity": 16,
        "borrowed_quantity": 4,
        "borrowers": 2,
    },
    {
        "id": 2,
        "name": "Pocket Compass",
        "total_quantity": 10,
        "available_quantity": 7,
        "borrowed_quantity": 3,
        "borrowers": 1,
    },
    {
        "id": 3,
        "name": "Swiss Army Knife",
        "total_quantity": 15,
        "available_quantity": 12,
        "borrowed_quantity": 3,
        "borrowers": 2,
    },
    {
        "id": 4,
        "name": "Flashlight",
        "total_quantity": 25,
        "available_quantity": 20,
        "borrowed_quantity": 5,
        "borrowers": 3,
    },
    {
        "id": 5,
        "name": "Binoculars",
        "total_quantity": 8,
        "available_quantity": 5,
        "borrowed_quantity": 3,
        "borrowers": 2,
    },
    {
        "id": 6,
        "name": "First Aid Kit",
        "total_quantity": 12,
        "available_quantity": 10,
        "borrowed_quantity": 2,
        "borrowers": 1,
    },
    {
        "id": 7,
        "name": "Water Bottle",
        "total_quantity": 30,
        "available_quantity": 25,
        "borrowed_quantity": 5,
        "borrowers": 4,
    },
    {
        "id": 8,
        "name": "Notebook",
        "total_quantity": 18,
        "available_quantity": 15,
        "borrowed_quantity": 3,
        "borrowers": 2,
    },
    {
        "id": 9,
        "name": "Sleeping Bag",
        "total_quantity": 10,
        "available_quantity": 7,
        "borrowed_quantity": 3,
        "borrowers": 2,
    },
    {
        "id": 10,
        "name": "Handheld GPS",
        "total_quantity": 5,
        "available_quantity": 3,
        "borrowed_quantity": 2,
        "borrowers": 1,
    },
]


@inventory_router.get("/inventory")
async def page(request: Request):
    return template(
        request,
        "inventory",
        {
            "role": "admin",
            "items": items,
        },
    )


@inventory_router.get("/items/{item_id}")
async def item(request: Request, item_id: int):
    return template(
        request,
        "item",
        {
            "id": item_id,
            "name": next(filter(lambda i: i["id"] == item_id, items))["name"],
        },
    )


@inventory_router.put("/items/{item_id}")
async def edit(
    item_id: int,
    name: Annotated[str, Body(embed=True)],
):
    item = next(filter(lambda i: i["id"] == item_id, items))
    item["name"] = name
    return "OK"


@inventory_router.delete("/items/{item_id}")
async def delete(item_id: int):
    item = next(filter(lambda i: i["id"] == item_id, items))
    items.remove(item)
    return "OK"
