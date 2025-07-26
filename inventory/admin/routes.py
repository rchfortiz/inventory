from http import HTTPStatus
from typing import Annotated

from bcrypt import gensalt, hashpw
from fastapi import APIRouter, Form, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from inventory.db.connection import DBSession
from inventory.db.models import Role, User
from inventory.templates.private import RenderTemplate, register_static_page
from inventory.user import Admin

admin_router = APIRouter(prefix="/admin")

register_static_page(admin_router, "/new-user", "admin/new_user")


@admin_router.get("")
async def index(
    _: Admin,
    db: DBSession,
    render_template: RenderTemplate,
) -> Response:
    users = db.exec(select(User)).all()
    return render_template("admin/index", {"users": users})


class NewUser(BaseModel):
    username: str
    password: str
    role: Role


@admin_router.post("/new-user")
async def new_user(
    _: Admin,
    db: DBSession,
    form: Annotated[NewUser, Form()],
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
    admin: Admin,
    db: DBSession,
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
