from typing import Annotated

from bcrypt import checkpw
from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlmodel import select

from inventory.db.connection import DBSession
from inventory.db.models import User
from inventory.templates.public import register_public_static_page, render_public_template

from .deps import Staff
from .token import give_token_and_redirect_to_items

user_router = APIRouter(prefix="/user")

register_public_static_page(user_router, "/login", "user/login")


class Login(BaseModel):
    username: str
    password: str


@user_router.post("/login")
async def login(
    request: Request,
    db: DBSession,
    form: Annotated[Login, Form()],
) -> Response:
    stmt = select(User).where(User.username == form.username)
    user = db.exec(stmt).first()

    if not user or not checkpw(form.password.encode(), user.password_hash):
        return render_public_template(
            request,
            "user/login",
            {"error": "Invalid username or password"},
        )

    return give_token_and_redirect_to_items(user)


@user_router.get("/sign-out")
async def sign_out(_: Staff) -> RedirectResponse:
    response = RedirectResponse("/user/login")
    response.delete_cookie("token")
    return response
