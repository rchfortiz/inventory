from http import HTTPStatus

from fastapi import HTTPException
from fastapi.responses import RedirectResponse

items_redirect = RedirectResponse("/items", HTTPStatus.SEE_OTHER)
items_redirect_exception = HTTPException(HTTPStatus.SEE_OTHER, headers={"Location": "/items"})
