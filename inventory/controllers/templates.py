from typing import Any

from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates("inventory/views")


def template(request: Request, name: str, data: dict[str, Any]):
    return templates.TemplateResponse(request, f"{name}.html.jinja", data)
