from collections.abc import Callable
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, Response
from fastapi.templating import Jinja2Templates

from inventory.routes.auth.dependencies import StaffDep

templates = Jinja2Templates("inventory/templates")


Context = dict[str, Any] | None


def _render_template(
    request: Request,
    user: StaffDep,
) -> "RenderTemplateFn":
    def inner(name: str, context: Context) -> Response:
        return templates.TemplateResponse(
            request,
            f"{name}.html.jinja",
            {"user": user, **(context or {})},
        )

    return inner


def render_public_template(request: Request, name: str, context: Context) -> Response:
    return templates.TemplateResponse(request, f"{name}.html.jinja", context or {})


RenderTemplateFn = Callable[[str, dict[str, Any] | None], Response]
RenderTemplate = Annotated[RenderTemplateFn, Depends(_render_template)]


def register_static_page(router: APIRouter, path: str, name: str) -> None:
    """`GET path` -> `inventory/templates/name.html.jinja`"""

    async def handle(render_template: RenderTemplate) -> Response:
        return render_template(name, {})

    router.get(path)(handle)


def register_public_static_page(router: APIRouter, path: str, name: str) -> None:
    """`GET path` -> `inventory/templates/name.html.jinja`"""

    async def handle(request: Request) -> Response:
        return render_public_template(request, name, {})

    router.get(path)(handle)
