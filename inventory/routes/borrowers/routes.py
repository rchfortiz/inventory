from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse

from inventory.db.connection import DBSessionDep
from inventory.db.models import Borrower, Log
from inventory.frontend import register_static_page
from inventory.routes import items_redirect
from inventory.routes.auth.dependencies import StaffDep

borrowers_router = APIRouter(prefix="/borrowers")

register_static_page(borrowers_router, "/add", "borrowers/add")


@borrowers_router.post("/add")
async def add_borrower(
    db: DBSessionDep,
    staff: StaffDep,
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

    return items_redirect
