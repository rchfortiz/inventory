from http.client import SEE_OTHER
from typing import Annotated

import jwt
from bcrypt import checkpw
from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from inventory.controllers.templates import template
from inventory.database import DatabaseDep
from inventory.services.user import get_user
from inventory.settings import settings

login_router = APIRouter()


@login_router.get("/login")
async def login_page(request: Request):
    return template(request, "login")


@login_router.post("/login")
async def log_in(
    request: Request,
    db: DatabaseDep,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    user = await get_user(db, username)
    if user is None:
        return template(request, "login", {"error": "Invalid username"})

    if not checkpw(password.encode(), user.password_hash):
        return template(request, "login", {"error": "Invalid password"})

    token = jwt.encode(
        {"name": user.name, "role": user.role},
        settings.jwt_secret_key,
        settings.jwt_algorithm,
    )

    resp = RedirectResponse("/inventory", SEE_OTHER)
    resp.set_cookie("token", token, httponly=True, secure=True)
    return resp
