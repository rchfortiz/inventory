from http import HTTPStatus

from bcrypt import gensalt, hashpw
from fastapi import APIRouter, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from inventory.db.connection import DBSessionDep
from inventory.db.models import User
from inventory.frontend import RenderTemplate, register_static_page
from inventory.routes.admin.schemas import NewUserForm
from inventory.routes.auth.dependencies import AdminDep

admin_router = APIRouter(prefix="/admin")

register_static_page(admin_router, "/new-user", "admin/new_user")


@admin_router.get("")
async def index(
    _: AdminDep,
    db: DBSessionDep,
    render_template: RenderTemplate,
) -> Response:
    users = db.exec(select(User)).all()
    return render_template("admin/index", {"users": users})


@admin_router.post("/new-user")
async def new_user(
    _: AdminDep,
    db: DBSessionDep,
    form: NewUserForm,
    render_template: RenderTemplate,
) -> Response:
    user = User(
        username=form.username,
        password_hash=hashpw(form.password.encode(), gensalt()),
        role=form.role,
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        return render_template("admin/new_user", {"error": "User already exists"})

    return RedirectResponse("/admin", HTTPStatus.SEE_OTHER)


@admin_router.get("/delete-user/{username}")
async def delete_user(
    admin: AdminDep,
    db: DBSessionDep,
    username: str,
    render_template: RenderTemplate,
) -> Response:
    if admin.username == username:
        return render_template("admin/index", {"error": "Cannot delete yourself"})

    user = db.exec(select(User).where(User.username == username)).first()
    if user is None:
        return render_template("admin/index", {"error": "Unknown user"})

    db.delete(user)
    db.commit()

    return RedirectResponse("/admin", HTTPStatus.SEE_OTHER)
