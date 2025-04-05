from bcrypt import checkpw
from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse
from sqlmodel import select

from inventory.db.connection import DBSessionDep
from inventory.db.models import User
from inventory.frontend import register_public_static_page, render_public_template
from inventory.routes.auth.dependencies import StaffDep
from inventory.routes.auth.schemas import LoginForm
from inventory.routes.auth.token import give_token_and_redirect_to_items

auth_router = APIRouter(prefix="/auth")

register_public_static_page(auth_router, "/login", "auth/login")


@auth_router.post("/login")
async def login(request: Request, db: DBSessionDep, form: LoginForm) -> Response:
    stmt = select(User).where(User.username == form.username)
    user = db.exec(stmt).first()

    if not user or not checkpw(form.password.encode(), user.password_hash):
        return render_public_template(
            request,
            "auth/login",
            {"error": "Invalid username or password"},
        )

    return give_token_and_redirect_to_items(user)


@auth_router.get("/sign-out")
async def sign_out(_: StaffDep) -> RedirectResponse:
    response = RedirectResponse("/auth/login")
    response.delete_cookie("token")
    return response
