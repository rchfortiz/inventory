from bcrypt import checkpw, gensalt, hashpw
from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse
from sqlmodel import select

from inventory.db.connection import DBSessionDep
from inventory.db.models import Role, User
from inventory.frontend import register_static_page, render_template
from inventory.routes.auth.dependencies import AdminDep, StaffDep
from inventory.routes.auth.schemas import LoginForm, RegisterForm
from inventory.routes.auth.token import give_token_and_redirect_to_items

auth_router = APIRouter(prefix="/auth")

register_static_page(auth_router, "/login", "auth/login")
register_static_page(auth_router, "/register", "auth/register")


@auth_router.post("/login")
async def login(request: Request, db: DBSessionDep, form: LoginForm) -> Response:
    stmt = select(User).where(User.username == form.username)
    user = db.exec(stmt).first()

    if not user:
        return render_template(request, "auth/login", {"error": "Invalid username or password"})

    if not checkpw(form.password.encode(), user.password_hash):
        return render_template(request, "auth/login", {"error": "Invalid username or password"})

    return give_token_and_redirect_to_items(user)


@auth_router.post("/register")
async def register(_: AdminDep, db: DBSessionDep, form: RegisterForm) -> Response:
    user = User(
        username=form.username,
        password_hash=hashpw(form.password.encode(), gensalt()),
        role=Role.STAFF,
    )
    db.add(user)
    db.commit()

    return give_token_and_redirect_to_items(user)


@auth_router.get("/sign-out")
async def sign_out(_: StaffDep) -> RedirectResponse:
    response = RedirectResponse("/auth/login")
    response.delete_cookie("token")
    return response
