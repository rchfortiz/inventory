from collections.abc import Callable
from http import HTTPStatus
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request
from pydantic import ValidationError

from inventory.db.models import Role
from inventory.routes.auth.token import TokenClaims
from inventory.settings import settings

redirect_to_login = HTTPException(HTTPStatus.SEE_OTHER, headers={"Location": "/auth/login"})


def get_user(request: Request) -> TokenClaims:
    token = request.cookies.get("token")
    if not token:
        raise redirect_to_login

    claims = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

    try:
        return TokenClaims.model_validate(claims)
    except ValidationError as err:
        raise redirect_to_login from err


def get_user_with_role(role: Role) -> Callable[[Request], TokenClaims]:
    def inner(request: Request) -> TokenClaims:
        claims = get_user(request)
        if claims.role >= role:
            return claims
        raise redirect_to_login

    return inner


StaffDep = Annotated[TokenClaims, Depends(get_user_with_role(Role.STAFF))]
AdminDep = Annotated[TokenClaims, Depends(get_user_with_role(Role.ADMIN))]
