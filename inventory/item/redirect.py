from http import HTTPStatus

from fastapi import HTTPException
from fastapi.responses import RedirectResponse

redirect_to_items = RedirectResponse("/items", HTTPStatus.SEE_OTHER)
redirect_to_items_exception = HTTPException(HTTPStatus.SEE_OTHER, headers={"Location": "/items"})
