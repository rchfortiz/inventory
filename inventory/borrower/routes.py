from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse

from inventory.db.connection import DBSession
from inventory.db.models import Borrower, Log
from inventory.item import redirect_to_items
from inventory.templates.private import register_static_page
from inventory.user import Staff

borrower_router = APIRouter(prefix="/borrower")

register_static_page(borrower_router, "/add", "borrowers/add")


@borrower_router.post("/add")
async def add_borrower(
    staff: Staff,
    db: DBSession,
    borrower: Annotated[Borrower, Form()],
) -> RedirectResponse:
    db.add(borrower)
    db.commit()

    log = Log(
        username=staff.username,
        action=f"Added borrower {borrower.name} (ID {borrower.id})",
    )
    db.add(log)
    db.commit()

    return redirect_to_items
