from http import HTTPStatus

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from sqlmodel import select

from inventory.db.connection import DBSessionDep
from inventory.db.models import Borrow, Borrower, Item
from inventory.frontend import register_static_page, render_template
from inventory.routes import items_redirect
from inventory.routes.auth.dependencies import StaffDep, get_user
from inventory.routes.items.dependencies import ItemDep
from inventory.routes.items.schemas import AddItemForm, BorrowItemForm, EditItemForm

items_router = APIRouter(prefix="/items", dependencies=[Depends(get_user)])


@items_router.get("/")
async def items_page(request: Request, db: DBSessionDep, user: StaffDep) -> Response:
    items = db.exec(select(Item)).all()
    return render_template(request, "items/all", {"items": items, "username": user.username})


register_static_page(items_router, "/add", "items/add")


@items_router.post("/add")
async def add_item(request: Request, db: DBSessionDep, form: AddItemForm) -> Response:
    if form.quantity < 1:
        error = "Attempted to add item with zero or negative quantity"
        return render_template(request, "items/add", {"error": error})

    item = Item(name=form.name, total_qty=form.quantity)
    db.add(item)
    db.commit()
    return items_redirect


@items_router.get("/{item_id}")
async def item_page(request: Request, item: ItemDep) -> Response:
    return render_template(request, "items/view", {"item": item})


@items_router.get("/{item_id}/delete")
async def delete_item(db: DBSessionDep, item: ItemDep) -> Response:
    db.delete(item)
    db.commit()

    return items_redirect


@items_router.get("/{item_id}/edit")
async def edit_item_page(request: Request, item: ItemDep) -> Response:
    return render_template(request, "items/edit", {"item": item})


@items_router.post("/{item_id}/edit")
async def edit_item(db: DBSessionDep, item: ItemDep, form: EditItemForm) -> Response:
    item.name = form.name
    db.commit()
    return items_redirect


@items_router.get("/{item_id}/borrow")
async def borrow_item_page(request: Request, db: DBSessionDep, item: ItemDep) -> Response:
    borrowers = db.exec(select(Borrower)).all()
    return render_template(request, "items/borrow", {"item": item, "borrowers": borrowers})


@items_router.post("/{item_id}/borrow")
async def borrow_item(
    request: Request,
    db: DBSessionDep,
    item: ItemDep,
    form: BorrowItemForm,
) -> Response:
    borrowers = db.exec(select(Borrower)).all()

    if form.quantity > item.available_qty:
        error = "Attempted to borrow more than available"
        return render_template(
            request,
            "items/borrow",
            {"item": item, "borrowers": borrowers, "error": error},
        )

    borrow = Borrow(item_id=item.id, borrower_id=form.borrower_id, qty=form.quantity)
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
