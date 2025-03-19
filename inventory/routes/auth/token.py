from http import HTTPStatus

import jwt
from fastapi import Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from inventory.db.models import Role, User
from inventory.settings import settings


class TokenClaims(BaseModel):
    username: str
    role: Role


def give_token_and_redirect_to_items(user: User) -> Response:
    response = RedirectResponse("/items", HTTPStatus.SEE_OTHER)

    claims = {"username": user.username, "role": user.role}
    token = jwt.encode(claims, settings.jwt_secret_key, settings.jwt_algorithm)
    response.set_cookie("token", token, secure=True, httponly=True)

    return response
