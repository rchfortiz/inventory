from fastapi import APIRouter, Request, Response

from . import Context, templates


def render_public_template(request: Request, name: str, context: Context = None) -> Response:
    return templates.TemplateResponse(request, f"{name}.html.jinja", context or {})


def register_public_static_page(router: APIRouter, path: str, name: str) -> None:
    """`GET path` -> `inventory/templates/name.html.jinja`"""

    async def handle(request: Request) -> Response:
        return render_public_template(request, name, {})

    router.get(path)(handle)
