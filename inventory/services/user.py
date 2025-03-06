from dataclasses import dataclass
from http.client import TEMPORARY_REDIRECT
from typing import Annotated, Literal, NoReturn, cast

import jwt
from bcrypt import gensalt, hashpw
from fastapi import Depends, HTTPException, Request

from inventory.database import database
from inventory.settings import settings

Role = Literal["staff", "admin"]


@dataclass(frozen=True)
class User:
    name: str
    role: Role


def get_user(request: Request) -> User:
    token = request.cookies.get("token")
    if token is None:
        redirect_to_login()

    try:
        claims = jwt.decode(token, settings.jwt_secret_key, [settings.jwt_algorithm])
    except jwt.DecodeError:
        redirect_to_login()
    if not isinstance(claims, dict):
        redirect_to_login()

    name = cast(str | None, claims.get("name"))
    role = cast(str | None, claims.get("role"))
    if name is None or role not in ("staff", "admin"):
        redirect_to_login()

    return User(name, role)


def get_admin(request: Request) -> User:
    user = get_user(request)
    if user.role != "admin":
        return redirect_to_login()
    return user


GetUserDep = Annotated[User, Depends(get_user)]
GetAdminDep = Annotated[User, Depends(get_admin)]


async def create_user(username: str, password: str, role: Role):
    password_hash = hashpw(password.encode(), gensalt())

    await database.execute(
        """
        INSERT INTO users
            (name, password_hash, role)
        VALUES
            (:name, :password_hash, :role)
        """,
        {"name": username, "password_hash": password_hash, "role": role},
    )


def redirect_to_login() -> NoReturn:
    raise HTTPException(TEMPORARY_REDIRECT, headers={"Location": "/login"})
