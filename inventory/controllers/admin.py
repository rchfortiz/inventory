from http.client import SEE_OTHER
from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from inventory.controllers.templates import template
from inventory.services.user import GetAdminDep, Role, create_user

admin_router = APIRouter()


@admin_router.get("/admin")
async def admin_page(_: GetAdminDep, request: Request):
    return template(request, "admin")


@admin_router.get("/admin/new-user")
async def new_user_page(_: GetAdminDep, request: Request):
    return template(request, "new_user")


@admin_router.post("/admin/new-user")
async def new_user(
    _: GetAdminDep,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    role: Annotated[Role, Form()],
):
    await create_user(username, password, role)
    return RedirectResponse("/admin", SEE_OTHER)
