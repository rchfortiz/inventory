from collections.abc import Generator
from dataclasses import dataclass
from http.client import TEMPORARY_REDIRECT
from typing import Annotated, Literal

import jwt
from fastapi import Depends, HTTPException, Request

from inventory.settings import settings


@dataclass(frozen=True)
class User:
    name: str
    role: Literal["staff", "admin"]


def get_user(request: Request) -> Generator[User]:
    token = request.cookies.get("token")
    if token is None:
        redirect_to_login()

    try:
        claims = jwt.decode(token, settings.jwt_secret_key, [settings.jwt_algorithm])
    except jwt.DecodeError:
        redirect_to_login()
    if not isinstance(claims, dict):
        redirect_to_login()

    name = claims.get("name")
    role = claims.get("role")
    if name is None or role is None:
        redirect_to_login()

    return User(name, role)


GetUserDep = Annotated[User, Depends(get_user)]


def redirect_to_login():
    raise HTTPException(TEMPORARY_REDIRECT, headers={"Location": "/login"})
