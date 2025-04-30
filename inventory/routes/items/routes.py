from http import HTTPStatus

from fastapi import APIRouter, Depends, Response
from fastapi.responses import RedirectResponse
from sqlmodel import select

from inventory.db.connection import DBSessionDep
from inventory.db.models import Borrow, Borrower, Item
from inventory.frontend import RenderTemplate
from inventory.routes import items_redirect
from inventory.routes.auth.dependencies import AdminDep, get_user
from inventory.routes.items.dependencies import ItemDep
from inventory.routes.items.schemas import AddItemForm, BorrowItemForm, EditItemForm

items_router = APIRouter(prefix="/items", dependencies=[Depends(get_user)])


@items_router.get("/")
async def items_page(db: DBSessionDep, render_template: RenderTemplate) -> Response:
    items = db.exec(select(Item).order_by(Item.category != "Consumable Supplies")).all()
    return render_template("items/all", {"items": items})


@items_router.get("/add")
async def add_item_page(_: AdminDep, render_template: RenderTemplate) -> Response:
    return render_template("items/add", {})


@items_router.post("/add")
async def add_item(
    _: AdminDep,
    db: DBSessionDep,
    form: AddItemForm,
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
    return items_redirect


@items_router.get("/{item_id}")
async def item_page(item: ItemDep, render_template: RenderTemplate) -> Response:
    return render_template("items/view", {"item": item})


@items_router.get("/{item_id}/delete")
async def delete_item(_: AdminDep, db: DBSessionDep, item: ItemDep) -> Response:
    db.delete(item)
    db.commit()

    return items_redirect


@items_router.get("/{item_id}/edit")
async def edit_item_page(item: ItemDep, render_template: RenderTemplate) -> Response:
    return render_template("items/edit", {"item": item})


@items_router.post("/{item_id}/edit")
async def edit_item(db: DBSessionDep, item: ItemDep, form: EditItemForm) -> Response:
    item.name = form.name
    item.description = form.description
    item.location = form.location
    db.commit()
    return items_redirect


@items_router.get("/{item_id}/borrow")
async def borrow_item_page(
    db: DBSessionDep,
    item: ItemDep,
    render_template: RenderTemplate,
) -> Response:
    borrowers = db.exec(select(Borrower)).all()
    return render_template("items/borrow", {"item": item, "borrowers": borrowers})


@items_router.post("/{item_id}/borrow")
async def borrow_item(
    db: DBSessionDep,
    item: ItemDep,
    form: BorrowItemForm,
    render_template: RenderTemplate,
) -> Response:
    borrowers = db.exec(select(Borrower)).all()

    if form.quantity > item.available_qty:
        error = "Attempted to borrow more than available"
        return render_template(
            "items/borrow",
            {"item": item, "borrowers": borrowers, "error": error},
        )

    borrow = Borrow(
        item_id=item.id,
        borrower_id=form.borrower_id,
        qty=form.quantity,
        due_date=form.due_date,
    )
    db.add(borrow)
    db.commit()
    return RedirectResponse(f"/items/{item.id}", HTTPStatus.SEE_OTHER)


@items_router.get("/{item_id}/borrows/{borrow_id}/delete")
async def return_item(db: DBSessionDep, item: ItemDep, borrow_id: int) -> Response:
    stmt = select(Borrow).where(Borrow.id == borrow_id)
    borrow = db.exec(stmt).first()
    if borrow:
        db.delete(borrow)
        db.commit()
    return RedirectResponse(f"/items/{item.id}", HTTPStatus.SEE_OTHER)
