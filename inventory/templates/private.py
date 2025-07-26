from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from inventory.user import Staff

from . import Context, templates


def _render_template(
    request: Request,
    user: Staff,
) -> "RenderTemplateFn":
    def inner(name: str, context: Context) -> Response:
        return templates.TemplateResponse(
            request,
            f"{name}.html.jinja",
            {"user": user, **(context or {})},
        )

    return inner


RenderTemplateFn = Callable[[str, dict[str, object] | None], Response]
RenderTemplate = Annotated[RenderTemplateFn, Depends(_render_template)]


def register_static_page(router: APIRouter, path: str, name: str) -> None:
    """`GET path` -> `inventory/templates/name.html.jinja`"""

    async def handle(render_template: RenderTemplate) -> Response:
        return render_template(name, {})

    router.get(path)(handle)
