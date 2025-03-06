from dataclasses import dataclass
from http.client import TEMPORARY_REDIRECT
from typing import Annotated, Literal, NoReturn, cast

import jwt
from bcrypt import gensalt, hashpw
from databases import Database
from fastapi import Depends, HTTPException, Request

from inventory.settings import settings

Role = Literal["staff", "admin"]


@dataclass(frozen=True)
class User:
    name: str
    password_hash: bytes
    role: Role


def get_user_dep(request: Request) -> User:
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

    return User(name=name, password_hash=b"", role=role)


def get_admin_dep(request: Request) -> User:
    user = get_user_dep(request)
    if user.role != "admin":
        return redirect_to_login()
    return user


GetUserDep = Annotated[User, Depends(get_user_dep)]
GetAdminDep = Annotated[User, Depends(get_admin_dep)]


async def get_user(db: Database, username: str) -> User | None:
    user = await db.fetch_one(
        """
        SELECT name, password_hash, role
        FROM users
        WHERE name = :name
        """,
        {"name": username},
    )
    return cast(User, user)


async def create_user(db: Database, username: str, password: str, role: Role):
    password_hash = hashpw(password.encode(), gensalt())

    await db.execute(
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
