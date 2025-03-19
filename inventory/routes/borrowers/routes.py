from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse

from inventory.db.connection import DBSessionDep
from inventory.db.models import Borrower
from inventory.frontend import register_static_page
from inventory.routes import items_redirect
from inventory.routes.auth.dependencies import get_user

borrowers_router = APIRouter(prefix="/borrowers", dependencies=[Depends(get_user)])

register_static_page(borrowers_router, "/add", "borrowers/add")


@borrowers_router.post("/add")
async def add_borrower(db: DBSessionDep, borrower: Annotated[Borrower, Form()]) -> RedirectResponse:
    db.add(borrower)
    db.commit()
    return items_redirect
