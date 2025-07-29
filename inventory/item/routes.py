from datetime import datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlmodel import select

from inventory.db.connection import DBSession
from inventory.db.models import Borrow, Borrower, Item, Log
from inventory.templates.private import RenderTemplate
from inventory.user import Admin, Staff

from .deps import ItemDep
from .redirect import redirect_to_items

item_router = APIRouter(prefix="/items")


@item_router.get("/")
async def items_page(_: Staff, db: DBSession, render_template: RenderTemplate) -> Response:
    items = db.exec(select(Item).order_by(Item.category != "Consumable Supplies")).all()  # pyright: ignore[reportArgumentType]
    return render_template("items/all", {"items": items})


@item_router.get("/add")
async def add_item_page(_: Admin, render_template: RenderTemplate) -> Response:
    return render_template("items/add", {})


class AddItem(BaseModel):
    name: str
    description: str
    category: str
    location: str
    quantity: int


@item_router.post("/add")
async def add_item(
    admin: Admin,
    db: DBSession,
    form: Annotated[AddItem, Form()],
    render_template: RenderTemplate,
) -> Response:
    if form.quantity < 1:
        error = "Attempted to add item with zero or negative quantity"
        return render_template("items/add", {"error": error})

    item = Item(
        name=form.name,
        description=form.description,
        category=form.category,
        location=form.location,
        total_qty=form.quantity,
    )
    db.add(item)
    db.commit()

    log = Log(username=admin.username, action=f'Created item "{item.name}" (ID {item.id})')
    db.add(log)
    db.commit()

    return redirect_to_items


@item_router.get("/{item_id}")
async def item_page(item: ItemDep, render_template: RenderTemplate) -> Response:
    return render_template("items/view", {"item": item})


@item_router.get("/{item_id}/delete")
async def delete_item(admin: Admin, db: DBSession, item: ItemDep) -> Response:
    borrow_exists = db.exec(select(Borrow).where(Borrow.item_id == item.id)).first()
    if borrow_exists:
        raise HTTPException(
            status_code=400,
            detail="Item is currently borrowed and cannot be deleted.",
        )

    db.delete(item)
    db.commit()

    log = Log(username=admin.username, action=f'Deleted item "{item.name}" (ID {item.id})')
    db.add(log)
    db.commit()

    return redirect_to_items


@item_router.get("/{item_id}/edit")
async def edit_item_page(item: ItemDep, render_template: RenderTemplate) -> Response:
    return render_template("items/edit", {"item": item})


class EditItem(BaseModel):
    name: str
    description: str
    location: str


@item_router.post("/{item_id}/edit")
async def edit_item(
    db: DBSession,
    staff: Staff,
    item: ItemDep,
    form: Annotated[EditItem, Form()],
) -> Response:
    item.name = form.name
    item.description = form.description
    item.location = form.location
    db.commit()

    log = Log(username=staff.username, action=f'Edited item "{item.name}" (ID {item.id})')
    db.add(log)
    db.commit()

    return redirect_to_items


@item_router.get("/{item_id}/borrow")
async def borrow_item_page(
    db: DBSession,
    item: ItemDep,
    render_template: RenderTemplate,
) -> Response:
    borrowers = db.exec(select(Borrower)).all()
    return render_template("items/borrow", {"item": item, "borrowers": borrowers})


class BorrowItem(BaseModel):
    borrower_id: int
    quantity: int
    due_date: datetime


@item_router.post("/{item_id}/borrow")
async def borrow_item(
    db: DBSession,
    staff: Staff,
    item: ItemDep,
    form: Annotated[BorrowItem, Form()],
    render_template: RenderTemplate,
) -> Response:
    borrowers = db.exec(select(Borrower)).all()

    if form.quantity > item.available_qty:
        error = "Attempted to borrow more than available"
        return render_template(
            "items/borrow",
            {"item": item, "borrowers": borrowers, "error": error},
        )

    borrower = db.exec(select(Borrower).where(Borrower.id == form.borrower_id)).first()
    if borrower is None:
        error = "Unknown borrower"
        return render_template(
            "items/borrow",
            {"item": item, "borrowers": borrowers, "error": error},
        )

    borrow = Borrow(
        item_id=item.id,
        borrower_id=borrower.id,
        qty=form.quantity,
        due_date=form.due_date,
    )
    db.add(borrow)
    db.commit()

    log = Log(
        username=staff.username,
        action=(
            f"Let borrower {borrower.name} (ID {borrower.id})"
            f" borrow (ID {borrow.id}) {borrow.qty} of {item.name} (ID {item.id})"
        ),
    )
    db.add(log)
    db.commit()

    return RedirectResponse(f"/items/{item.id}", HTTPStatus.SEE_OTHER)


@item_router.get("/{item_id}/borrows/{borrow_id}/delete")
async def return_item(db: DBSession, staff: Staff, item: ItemDep, borrow_id: int) -> Response:
    stmt = select(Borrow).where(Borrow.id == borrow_id)
    borrow = db.exec(stmt).first()
    if borrow:
        db.delete(borrow)
        db.commit()

    log = Log(
        username=staff.username,
        action=f"Returned borrow ID {borrow_id}",
    )
    db.add(log)
    db.commit()

    return RedirectResponse(f"/items/{item.id}", HTTPStatus.SEE_OTHER)
