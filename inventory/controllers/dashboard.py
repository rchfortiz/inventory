from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from inventory.controllers.templates import template

dashboard_router = APIRouter()

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


@dashboard_router.get("/dashboard")
async def page(request: Request):
    return template(
        request,
        "dashboard",
        {
            "role": "admin",
            "items": items,
        },
    )


@dashboard_router.get("/edit/{item_id}")
async def edit_page(request: Request, item_id: int):
    return template(
        request,
        "edit",
        {
            "id": item_id,
            "name": next(filter(lambda i: i["id"] == item_id, items))["name"],
        },
    )


@dashboard_router.post("/edit/{item_id}")
async def edit(
    item_id: int,
    name: Annotated[str, Form()],
):
    item = next(filter(lambda i: i["id"] == item_id, items))
    item["name"] = name
    return RedirectResponse("/dashboard", 303)


@dashboard_router.post("/delete/{item_id}")
async def delete(item_id: int):
    item = next(filter(lambda i: i["id"] == item_id, items))
    items.remove(item)
    return RedirectResponse("/dashboard", 303)
